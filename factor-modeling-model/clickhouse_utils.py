import pandas as pd
import traceback
from clickhouse_driver import Client
from datetime import datetime

class ClickHouseUtils:
    """Utility class for ClickHouse operations"""
    
    def __init__(self, host='44.222.122.134', port=9000, user='jacky_user', password='your_secure_password', database='jacky_database1'):
        """Initialize the ClickHouse client"""
        self.client = Client(host=host, port=port, user=user, password=password, database=database)
        self.database = database
    
    def create_factor_tables(self):
        """Create tables for storing factor analysis results"""
        try:
            # Create factor_summary table
            self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.database}.factor_summary (
                factor_id UUID DEFAULT generateUUIDv4(),
                factor_name String,
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
                description String
            ) ENGINE = MergeTree()
            ORDER BY (factor_name, test_date)
            """)
            
            # Create factor_details table
            self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.database}.factor_details (
                detail_id UUID DEFAULT generateUUIDv4(),
                factor_id UUID,
                ticker String,
                beta Float64,
                tstat Float64,
                pvalue Float64,
                rsquared Float64,
                conf_int_lower Float64,
                conf_int_upper Float64
            ) ENGINE = MergeTree()
            ORDER BY (factor_id, ticker)
            """)
            
            # Create factor_timeseries table
            self.client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.database}.factor_timeseries (
                ts_id UUID DEFAULT generateUUIDv4(),
                factor_id UUID,
                date Date,
                factor_value Float64,
                high_portfolio_return Float64,
                low_portfolio_return Float64
            ) ENGINE = MergeTree()
            ORDER BY (factor_id, date)
            """)
            
            print("Factor tables created successfully")
            return True
            
        except Exception as e:
            print(f"Error creating factor tables: {str(e)}")
            print(traceback.format_exc())
            return False
    
    def get_all_factors(self):
        """Get summary of all factors in the database"""
        try:
            query = """
            SELECT 
                factor_id,
                factor_name,
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
                max_drawdown
            FROM factor_summary
            ORDER BY test_date DESC
            """
            
            result = self.client.execute(query, with_column_types=True)
            columns = [col[0] for col in result[1]]
            df = pd.DataFrame(result[0], columns=columns)
            
            return df
            
        except Exception as e:
            print(f"Error getting factors: {str(e)}")
            print(traceback.format_exc())
            return pd.DataFrame()
    
    def get_factor_details(self, factor_id):
        """Get detailed results for a specific factor"""
        try:
            # Get summary
            summary_query = f"""
            SELECT * FROM factor_summary WHERE factor_id = '{factor_id}'
            """
            summary_result = self.client.execute(summary_query, with_column_types=True)
            summary_columns = [col[0] for col in summary_result[1]]
            summary = pd.DataFrame(summary_result[0], columns=summary_columns)
            
            # Get details
            details_query = f"""
            SELECT * FROM factor_details WHERE factor_id = '{factor_id}'
            """
            details_result = self.client.execute(details_query, with_column_types=True)
            details_columns = [col[0] for col in details_result[1]]
            details = pd.DataFrame(details_result[0], columns=details_columns)
            
            # Get time series
            ts_query = f"""
            SELECT * FROM factor_timeseries WHERE factor_id = '{factor_id}'
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
    
    def compare_factors(self, factor_names=None):
        """
        Compare multiple factors
        
        Parameters:
        - factor_names: List of factor names to compare. If None, compare all factors.
        
        Returns:
        - DataFrame with comparison metrics
        """
        try:
            if factor_names:
                factor_list = "', '".join(factor_names)
                where_clause = f"WHERE factor_name IN ('{factor_list}')"
            else:
                where_clause = ""
            
            query = f"""
            SELECT 
                factor_id,
                factor_name,
                test_date,
                avg_beta,
                avg_tstat,
                avg_rsquared,
                significant_stocks,
                total_stocks,
                annualized_return,
                annualized_volatility,
                sharpe_ratio,
                max_drawdown
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
    
    def close(self):
        """Close the client connection"""
        self.client.disconnect()


# Example usage
if __name__ == "__main__":
    # Create a utils instance
    utils = ClickHouseUtils()
    
    # Create factor tables
    utils.create_factor_tables()
    
    # Get all factors
    factors = utils.get_all_factors()
    print("Factors in database:")
    print(factors)
    
    # Close connection
    utils.close()
