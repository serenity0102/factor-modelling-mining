import pandas as pd
import numpy as np
import traceback
from datetime import datetime, date
from clickhouse_driver import Client


class ClickHouseUtils:
    """Utility class for ClickHouse operations"""

    def __init__(self, host='44.222.122.134', port=9000, user='user', password='password',
                 database='factor_model_tick_data_database'):
        """Initialize ClickHouse connection"""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        try:
            self.client = Client(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print(f"Connected to ClickHouse at {self.host}:{self.port}")
        except Exception as e:
            print(f"Error connecting to ClickHouse: {str(e)}")
            print(traceback.format_exc())
            self.client = None

    def close(self):
        """Close ClickHouse connection"""
        if self.client:
            self.client = None
            print("ClickHouse connection closed")

    def create_factor_tables(self):
        """Create tables for storing factor analysis results"""
        try:
            # Create factor_summary table
            self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.database}.factor_summary (
                factor_name String,
                factor_type String,
                test_date Date,
                start_date Date,
                end_date Date,
                avg_beta Float64,
                avg_tstat Float64,
                avg_rsquared Float64,
                significant_stocks Int32,
                total_stocks Int32,
                annualized_return Float64,
                annualized_volatility Float64,
                sharpe_ratio Float64,
                max_drawdown Float64,
                description String,
                update_time DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (factor_type, factor_name, test_date)
            """)

            # Create factor_details table
            self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.database}.factor_details (
                factor_name String,
                factor_type String,
                test_date Date,
                ticker String,
                beta Float64,
                tstat Float64,
                pvalue Float64,
                rsquared Float64,
                conf_int_lower Float64,
                conf_int_upper Float64,
                update_time DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (factor_name, factor_type, test_date, ticker)
            """)

            # Create factor_timeseries table
            self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.database}.factor_timeseries (
                factor_name String,
                factor_type String,
                date Date,
                factor_value Float64,
                high_portfolio_return Float64,
                low_portfolio_return Float64,
                update_time DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (factor_name, factor_type, date)
            """)

            # Create factor_values table for storing raw factor values
            self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.database}.factor_values (
                factor_type String,
                factor_name String,
                ticker String,
                date Date,
                value Float64,
                update_time DateTime DEFAULT now()
            ) ENGINE = MergeTree()
            ORDER BY (factor_type, factor_name, ticker, date)
            """)

            print("Factor tables created successfully")
            return True

        except Exception as e:
            print(f"Error creating factor tables: {str(e)}")
            print(traceback.format_exc())
            return False

    def store_factor_values(self, factor_type, factor_name, factor_df):
        """
        Store raw factor values in the database

        Parameters:
        - factor_type: Type of factor (e.g., 'Technical', 'Fundamental')
        - factor_name: Name of the factor (e.g., 'RSI14', 'PEG')
        - factor_df: DataFrame with factor values (index=dates, columns=tickers)

        Returns:
        - success: Boolean indicating if operation was successful
        """
        try:
            print(f"Storing {factor_name} values in ClickHouse...")

            # Prepare data for insertion
            data = []
            for date in factor_df.index:
                date_str = datetime.today()
                for ticker in factor_df.columns:
                    value = factor_df.loc[date, ticker]
                    if pd.notna(value):
                        data.append((
                            factor_type,
                            factor_name,
                            ticker,
                            date_str,
                            float(value)
                        ))

            if data:
                # Insert data into factor_values table using SQL directly
                # for item in data:
                #     self.client.execute(f"""
                #     INSERT INTO {self.database}.factor_values
                #     (factor_type, factor_name, ticker, date, value)
                #     VALUES ('{item[0]}', '{item[1]}', '{item[2]}', '{item[3]}', {item[4]})
                #     """)
                self.client.execute(
                    f"INSERT INTO {self.database}.factor_values "
                    "(factor_type, factor_name, ticker, date, value) VALUES",
                    data
                )
                print(f"Successfully stored {len(data)} {factor_name} values")
                return True
            else:
                print(f"No valid {factor_name} values to store")
                return False

        except Exception as e:
            print(f"Error storing factor values: {str(e)}")
            print(traceback.format_exc())
            return False

    def store_factor_results(self, factor_name, factor_type, results_dict, description=""):
        """
        Store factor test results in ClickHouse

        Parameters:
        - factor_name: Name of the factor
        - factor_type: Type of factor (e.g., 'Technical', 'Fundamental')
        - results_dict: Dictionary containing test results
        - description: Optional description of the factor

        Returns:
        - success: Boolean indicating if operation was successful
        """
        try:
            print(f"Storing {factor_name} factor results in ClickHouse...")

            # Extract data from results_dict
            factor_test_results = results_dict.get('factor_test_results', pd.DataFrame())
            performance_results = results_dict.get('performance_results', pd.DataFrame())
            portfolio_returns = results_dict.get('portfolio_returns', pd.DataFrame())

            # Prepare summary data
            # test_date = datetime.now().strftime('%Y-%m-%d')
            test_date = datetime.today()

            # Get date range from portfolio returns
            if not portfolio_returns.empty:
                start_date = portfolio_returns.index[0].strftime('%Y-%m-%d')
                end_date = portfolio_returns.index[-1].strftime('%Y-%m-%d')
            else:
                start_date = "2000-01-01"
                end_date = "2025-03-31"

            # Calculate summary statistics
            avg_beta = float(factor_test_results['Beta'].mean()) if 'Beta' in factor_test_results else 0.0
            avg_tstat = float(factor_test_results['T-stat'].mean()) if 'T-stat' in factor_test_results else 0.0
            avg_rsquared = float(factor_test_results['R-squared'].mean()) if 'R-squared' in factor_test_results else 0.0

            significant_stocks = int(
                (abs(factor_test_results['T-stat']) > 1.96).sum()) if 'T-stat' in factor_test_results else 0
            total_stocks = len(factor_test_results) if not factor_test_results.empty else 0

            # Get performance metrics
            factor_col = f'{factor_name}_Factor'
            if not performance_results.empty and 'Annualized Return' in performance_results and factor_col in \
                    performance_results['Annualized Return']:
                ann_return = float(performance_results['Annualized Return'][factor_col])
                ann_vol = float(performance_results['Annualized Volatility'][factor_col])
                sharpe = float(performance_results['Sharpe Ratio'][factor_col])
                max_dd = float(performance_results['Maximum Drawdown'][factor_col])
            else:
                ann_return = 0.0
                ann_vol = 0.0
                sharpe = 0.0
                max_dd = 0.0

            # Insert summary into database using SQL directly
            self.client.execute(f"""
            INSERT INTO {self.database}.factor_summary 
            (factor_name, factor_type, test_date, start_date, end_date, avg_beta, avg_tstat, avg_rsquared, 
             significant_stocks, total_stocks, annualized_return, annualized_volatility, 
             sharpe_ratio, max_drawdown, description)
            VALUES
            ('{factor_name}', '{factor_type}', '{test_date}', '{start_date}', '{end_date}', 
             {avg_beta}, {avg_tstat}, {avg_rsquared}, {significant_stocks}, {total_stocks}, 
             {ann_return}, {ann_vol}, {sharpe}, {max_dd}, 
             '{description or f"{factor_name} factor analysis results"}')
            """)
            print(f"Insert data into factor_summary table has DONE")

            if not factor_test_results.empty:
                detail_data = []

                for ticker, row in factor_test_results.iterrows():
                    beta = float(row.get('Beta', 0.0))
                    tstat = float(row.get('T-stat', 0.0))
                    pvalue = float(row.get('P-value', 0.0))
                    rsquared = float(row.get('R-squared', 0.0))
                    conf_int_lower = float(row.get('Conf_Int_Lower', 0.0))
                    conf_int_upper = float(row.get('Conf_Int_Upper', 0.0))

                    detail_data.append(
                        (factor_name, factor_type, test_date, ticker, beta, tstat, pvalue, rsquared, conf_int_lower,
                         conf_int_upper)
                    )

                # Execute for bulk insert
                query = f"""
                INSERT INTO {self.database}.factor_details
                (factor_name, factor_type, test_date, ticker, beta, tstat, pvalue, rsquared, conf_int_lower, conf_int_upper)
                VALUES
                """
                self.client.execute(query, detail_data)
                print("Insert into factor_details DONE")

            if not portfolio_returns.empty and factor_col in portfolio_returns.columns:
                timeseries_data = []

                for date, row in portfolio_returns.iterrows():
                    # date_str = date.strftime('%Y-%m-%d')
                    date_str = datetime.today()
                    factor_value = float(row.get(factor_col, 0.0))
                    high_return = float(row.get(f'High_{factor_name}', 0.0))
                    low_return = float(row.get(f'Low_{factor_name}', 0.0))

                    timeseries_data.append(
                        (factor_name, factor_type, date_str, factor_value, high_return, low_return)
                    )

                # Execute for bulk insert
                query = f"""
                INSERT INTO {self.database}.factor_timeseries 
                (factor_name, factor_type, date, factor_value, high_portfolio_return, low_portfolio_return)
                VALUES
                """
                self.client.execute(query, timeseries_data)
                print(f"Insert data into factor_timeseries table has DONE")

            print(f"Successfully stored {factor_name} factor results")
            return True

        except Exception as e:
            print(f"Error storing factor results: {str(e)}")
            print(traceback.format_exc())
            return False

    def get_all_factors(self):
        """Get summary of all factors in the database"""
        try:
            query = """
            SELECT 
                factor_name,
                factor_type,
                test_date,
                start_date,
                end_date,
                avg_beta,
                avg_tstat,
                avg_rsquared,
                significant_stocks,
                total_stocks,
                annualized_return,
                annualized_volatility,
                sharpe_ratio,
                max_drawdown,
                description,
                update_time
            FROM factor_summary
            ORDER BY factor_type, sharpe_ratio DESC
            """

            result = self.client.execute(query, with_column_types=True)
            columns = [col[0] for col in result[1]]
            df = pd.DataFrame(result[0], columns=columns)

            return df

        except Exception as e:
            print(f"Error getting factors: {str(e)}")
            print(traceback.format_exc())
            return pd.DataFrame()

    def get_factor_details(self, factor_name, factor_type, test_date):
        """Get detailed results for a specific factor"""
        try:
            # Get summary
            summary_query = f"""
            SELECT * FROM factor_summary 
            WHERE factor_name = '{factor_name}' 
            AND factor_type = '{factor_type}' 
            AND test_date = '{test_date}'
            """
            summary_result = self.client.execute(summary_query, with_column_types=True)
            summary_columns = [col[0] for col in summary_result[1]]
            summary = pd.DataFrame(summary_result[0], columns=summary_columns)

            # Get details
            details_query = f"""
            SELECT * FROM factor_details 
            WHERE factor_name = '{factor_name}' 
            AND factor_type = '{factor_type}' 
            AND test_date = '{test_date}'
            """
            details_result = self.client.execute(details_query, with_column_types=True)
            details_columns = [col[0] for col in details_result[1]]
            details = pd.DataFrame(details_result[0], columns=details_columns)

            # Get time series
            ts_query = f"""
            SELECT * FROM factor_timeseries 
            WHERE factor_name = '{factor_name}' 
            AND factor_type = '{factor_type}'
            ORDER BY date
            """
            ts_result = self.client.execute(ts_query, with_column_types=True)
            ts_columns = [col[0] for col in ts_result[1]]
            timeseries = pd.DataFrame(ts_result[0], columns=ts_columns)

            if not timeseries.empty:
                timeseries['date'] = pd.to_datetime(timeseries['date'])
                timeseries.set_index('date', inplace=True)

            return {
                'summary': summary,
                'details': details,
                'timeseries': timeseries
            }

        except Exception as e:
            print(f"Error getting factor details: {str(e)}")
            print(traceback.format_exc())
            return {
                'summary': pd.DataFrame(),
                'details': pd.DataFrame(),
                'timeseries': pd.DataFrame()
            }

    def compare_factors(self, factor_names=None, factor_types=None):
        """
        Compare multiple factors

        Parameters:
        - factor_names: List of factor names to compare. If None, compare all factors.
        - factor_types: List of factor types to compare. If None, compare all types.

        Returns:
        - DataFrame with comparison metrics
        """
        try:
            where_clauses = []

            if factor_names:
                factor_list = "', '".join(factor_names)
                where_clauses.append(f"factor_name IN ('{factor_list}')")

            if factor_types:
                type_list = "', '".join(factor_types)
                where_clauses.append(f"factor_type IN ('{type_list}')")

            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            query = f"""
            SELECT 
                factor_name,
                factor_type,
                test_date,
                avg_beta,
                avg_tstat,
                avg_rsquared,
                significant_stocks,
                total_stocks,
                annualized_return,
                annualized_volatility,
                sharpe_ratio,
                max_drawdown,
                update_time
            FROM factor_summary
            {where_clause}
            ORDER BY sharpe_ratio DESC
            """

            result = self.client.execute(query, with_column_types=True)
            columns = [col[0] for col in result[1]]
            df = pd.DataFrame(result[0], columns=columns)

            return df

        except Exception as e:
            print(f"Error comparing factors: {str(e)}")
            print(traceback.format_exc())
            return pd.DataFrame()

    def get_factor_values(self, factor_name, factor_type, start_date=None, end_date=None):
        """Get raw factor values for a specific factor"""
        try:
            where_clauses = [f"factor_name = '{factor_name}'", f"factor_type = '{factor_type}'"]

            if start_date:
                where_clauses.append(f"date >= '{start_date}'")

            if end_date:
                where_clauses.append(f"date <= '{end_date}'")

            where_clause = f"WHERE {' AND '.join(where_clauses)}"

            query = f"""
            SELECT ticker, date, value
            FROM factor_values
            {where_clause}
            ORDER BY ticker, date
            """

            result = self.client.execute(query, with_column_types=True)
            columns = [col[0] for col in result[1]]
            df = pd.DataFrame(result[0], columns=columns)

            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                # Pivot to get tickers as columns
                pivot_df = df.pivot(index='date', columns='ticker', values='value')
                return pivot_df

            return pd.DataFrame()

        except Exception as e:
            print(f"Error getting factor values: {str(e)}")
            print(traceback.format_exc())
            return pd.DataFrame()

    def delete_factor(self, factor_name, factor_type, test_date=None):
        """Delete a factor from all tables"""
        try:
            print(f"Deleting factor: {factor_name}, type: {factor_type}")

            where_clauses = [f"factor_name = '{factor_name}'", f"factor_type = '{factor_type}'"]

            if test_date:
                where_clauses.append(f"test_date = '{test_date}'")

            where_clause = f"WHERE {' AND '.join(where_clauses)}"

            # Delete from factor_summary
            self.client.execute(f"DELETE FROM {self.database}.factor_summary {where_clause}")

            # Delete from factor_details
            self.client.execute(f"DELETE FROM {self.database}.factor_details {where_clause}")

            # Delete from factor_timeseries (no test_date column)
            where_clause_ts = f"WHERE factor_name = '{factor_name}' AND factor_type = '{factor_type}'"
            self.client.execute(f"DELETE FROM {self.database}.factor_timeseries {where_clause_ts}")

            # Delete from factor_values (no test_date column)
            self.client.execute(f"DELETE FROM {self.database}.factor_values {where_clause_ts}")

            print(f"Successfully deleted factor: {factor_name}, type: {factor_type}")
            return True

        except Exception as e:
            print(f"Error deleting factor: {str(e)}")
            print(traceback.format_exc())
            return False