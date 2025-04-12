import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import traceback
from datetime import datetime
from djia_factor_analysis import run_peg_factor_analysis, ClickHouseDataFetcher, DJIA_TICKERS

def create_factor_dashboard(factor_name, data_fetcher):
    """Create a dashboard for factor analysis results"""
    try:
        print(f"Creating dashboard for factor: {factor_name}...")
        
        # Get factor summary
        summary_data = data_fetcher.client.execute(f"""
        SELECT * FROM jacky_database1.factor_summary WHERE factor_name = '{factor_name}'
        """)
        
        if not summary_data:
            print(f"No summary data found for factor ID: {factor_name}")
            return
        
        # Convert to DataFrame
        summary_columns = [
            'factor_name', 'test_date', 'start_date', 'end_date',
            'avg_beta', 'avg_tstat', 'avg_rsquared', 'significant_stocks', 'total_stocks',
            'annualized_return', 'annualized_volatility', 'sharpe_ratio', 'max_drawdown', 'description', 'update_date'
        ]
        summary = pd.DataFrame(summary_data, columns=summary_columns)
        
        # Get factor details
        details_data = data_fetcher.client.execute(f"""
        SELECT * FROM jacky_database1.factor_details WHERE factor_name = '{factor_name}'
        """)
        
        # Convert to DataFrame
        details_columns = [
            'factor_name', 'ticker', 'beta', 'tstat', 'pvalue', 'rsquared',
            'conf_int_lower', 'conf_int_upper', 'update_time'
        ]
        details = pd.DataFrame(details_data, columns=details_columns) if details_data else pd.DataFrame()
        
        # Get time series data
        timeseries_data = data_fetcher.client.execute(f"""
        SELECT * FROM jacky_database1.factor_timeseries WHERE factor_name = '{factor_name}'
        ORDER BY date
        """)
        
        # Convert to DataFrame
        timeseries_columns = [
            'factor_name', 'date', 'factor_value', 'high_portfolio_return', 'low_portfolio_return', 'update_time'
        ]
        timeseries = pd.DataFrame(timeseries_data, columns=timeseries_columns) if timeseries_data else pd.DataFrame()
        
        if not timeseries.empty:
            timeseries['date'] = pd.to_datetime(timeseries['date'])
            timeseries.set_index('date', inplace=True)
        
        # Create output directory
        os.makedirs('factor_dashboard', exist_ok=True)
        
        # Create dashboard HTML
        factor_name = summary['factor_name'].iloc[0]
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{factor_name} Factor Analysis Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 10px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 30px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .chart {{ margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{factor_name} Factor Analysis Dashboard</h1>
                <p>Test Date: {summary['test_date'].iloc[0]}</p>
                <p>Date Range: {summary['start_date'].iloc[0]} to {summary['end_date'].iloc[0]}</p>
            </div>
            
            <div class="section">
                <h2>Summary Statistics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Average Beta</td>
                        <td>{summary['avg_beta'].iloc[0]:.4f}</td>
                    </tr>
                    <tr>
                        <td>Average T-statistic</td>
                        <td>{summary['avg_tstat'].iloc[0]:.4f}</td>
                    </tr>
                    <tr>
                        <td>Average R-squared</td>
                        <td>{summary['avg_rsquared'].iloc[0]:.4f}</td>
                    </tr>
                    <tr>
                        <td>Significant Stocks</td>
                        <td>{summary['significant_stocks'].iloc[0]} out of {summary['total_stocks'].iloc[0]}</td>
                    </tr>
                    <tr>
                        <td>Annualized Return</td>
                        <td>{summary['annualized_return'].iloc[0]:.2%}</td>
                    </tr>
                    <tr>
                        <td>Annualized Volatility</td>
                        <td>{summary['annualized_volatility'].iloc[0]:.2%}</td>
                    </tr>
                    <tr>
                        <td>Sharpe Ratio</td>
                        <td>{summary['sharpe_ratio'].iloc[0]:.2f}</td>
                    </tr>
                    <tr>
                        <td>Maximum Drawdown</td>
                        <td>{summary['max_drawdown'].iloc[0]:.2%}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>Factor Performance</h2>
                <div class="chart">
                    <img src="../{factor_name.lower()}_factor_cumulative_returns_real_data.png" width="100%">
                </div>
            </div>
            
            <div class="section">
                <h2>Factor Statistics</h2>
                <div class="chart">
                    <img src="../{factor_name.lower()}_factor_statistics_real_data.png" width="100%">
                </div>
            </div>
        """
        
        # Add stock-level results if available
        if not details.empty:
            html_content += """
            <div class="section">
                <h2>Stock-Level Results</h2>
                <table>
                    <tr>
                        <th>Ticker</th>
                        <th>Beta</th>
                        <th>T-stat</th>
                        <th>P-value</th>
                        <th>R-squared</th>
                        <th>95% Confidence Interval</th>
                    </tr>
            """
            
            # Add rows for each stock
            for _, row in details.iterrows():
                html_content += f"""
                    <tr>
                        <td>{row['ticker']}</td>
                        <td>{row['beta']:.4f}</td>
                        <td>{row['tstat']:.4f}</td>
                        <td>{row['pvalue']:.4f}</td>
                        <td>{row['rsquared']:.4f}</td>
                        <td>[{row['conf_int_lower']:.4f}, {row['conf_int_upper']:.4f}]</td>
                    </tr>
                """
            
            html_content += """
                </table>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        # Write HTML to file
        with open(f'factor_dashboard/{factor_name.lower()}_factor_dashboard.html', 'w') as f:
            f.write(html_content)
        
        print(f"Dashboard created at: factor_dashboard/{factor_name.lower()}_factor_dashboard.html")
    except Exception as e:
        print(f"Error creating dashboard: {str(e)}")
        print(traceback.format_exc())

def main():
    """Main function to run DJIA factor analysis"""
    try:
        print("Starting DJIA factor analysis...")
        
        # Create data fetcher with the correct credentials
        data_fetcher = ClickHouseDataFetcher(
            host='44.222.122.134',
            port=9000,
            user='jacky_user',
            password='your_secure_password',
            database='jacky_database1'
        )
        
        # Run PEG factor analysis
        print("\n=== Running PEG Factor Analysis ===")
        peg_results = run_peg_factor_analysis()
        
        if peg_results:
            # Store results in ClickHouse
            peg_factor_name = data_fetcher.store_factor_results(
                factor_name="PEG",
                results_dict=peg_results,
                description="Price-to-Earnings to Growth ratio. Lower PEG indicates better value relative to growth."
            )
            
            if peg_factor_name:
                # Create dashboard
                create_factor_dashboard(peg_factor_name, data_fetcher)
                
                print(f"\nPEG factor analysis completed successfully. Factor name: {peg_factor_name}")
            else:
                print("\nFailed to store PEG factor results in ClickHouse.")
        else:
            print("\nPEG factor analysis failed.")
        
        # Close connection
        # data_fetcher.close()
        
        print("\nAll analyses completed.")
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
