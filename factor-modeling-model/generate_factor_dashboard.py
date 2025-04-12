import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import traceback
from clickhouse_utils import ClickHouseUtils

def generate_factor_comparison_dashboard(utils):
    """Generate a dashboard comparing all factors"""
    try:
        print("Generating factor comparison dashboard...")
        
        # Get all factors
        factors = utils.get_all_factors()
        
        if factors.empty:
            print("No factors found in the database")
            return
        
        # Create output directory
        os.makedirs('factor_dashboard', exist_ok=True)
        
        # Create comparison chart
        plt.figure(figsize=(12, 8))
        
        # Plot Sharpe ratios
        plt.subplot(2, 2, 1)
        sns.barplot(x='factor_name', y='sharpe_ratio', data=factors)
        plt.title('Sharpe Ratio by Factor')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Plot annualized returns
        plt.subplot(2, 2, 2)
        sns.barplot(x='factor_name', y='annualized_return', data=factors)
        plt.title('Annualized Return by Factor')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Plot average t-stats
        plt.subplot(2, 2, 3)
        sns.barplot(x='factor_name', y='avg_tstat', data=factors)
        plt.title('Average T-statistic by Factor')
        plt.xticks(rotation=45)
        plt.axhline(y=1.96, color='r', linestyle='--')
        plt.axhline(y=-1.96, color='r', linestyle='--')
        plt.tight_layout()
        
        # Plot average R-squared
        plt.subplot(2, 2, 4)
        sns.barplot(x='factor_name', y='avg_rsquared', data=factors)
        plt.title('Average R-squared by Factor')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save the figure
        plt.savefig('factor_dashboard/factor_comparison.png')
        
        # Create HTML dashboard
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Factor Comparison Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 10px; margin-bottom: 20px; }
                .section { margin-bottom: 30px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .chart { margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Factor Comparison Dashboard</h1>
                <p>Comparison of all factors in the database</p>
            </div>
            
            <div class="section">
                <h2>Factor Comparison Chart</h2>
                <div class="chart">
                    <img src="factor_comparison.png" width="100%">
                </div>
            </div>
            
            <div class="section">
                <h2>Factor Summary Table</h2>
                <table>
                    <tr>
                        <th>Factor Name</th>
                        <th>Test Date</th>
                        <th>Sharpe Ratio</th>
                        <th>Annualized Return</th>
                        <th>Annualized Volatility</th>
                        <th>Max Drawdown</th>
                        <th>Avg T-stat</th>
                        <th>Avg R-squared</th>
                        <th>Significant Stocks</th>
                    </tr>
        """
        
        # Add rows for each factor
        for _, row in factors.iterrows():
            html_content += f"""
                    <tr>
                        <td>{row['factor_name']}</td>
                        <td>{row['test_date']}</td>
                        <td>{row['sharpe_ratio']:.2f}</td>
                        <td>{row['annualized_return']:.2%}</td>
                        <td>{row['annualized_volatility']:.2%}</td>
                        <td>{row['max_drawdown']:.2%}</td>
                        <td>{row['avg_tstat']:.2f}</td>
                        <td>{row['avg_rsquared']:.2f}</td>
                        <td>{row['significant_stocks']} / {row['total_stocks']}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Individual Factor Dashboards</h2>
                <ul>
        """
        
        # Add links to individual factor dashboards
        for _, row in factors.iterrows():
            factor_name = row['factor_name']
            html_content += f"""
                    <li><a href="{factor_name.lower()}_factor_dashboard.html">{factor_name} Factor Dashboard</a></li>
            """
        
        html_content += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        # Write HTML to file
        with open('factor_dashboard/factor_comparison_dashboard.html', 'w') as f:
            f.write(html_content)
        
        print("Factor comparison dashboard created at: factor_dashboard/factor_comparison_dashboard.html")
    except Exception as e:
        print(f"Error generating factor comparison dashboard: {str(e)}")
        print(traceback.format_exc())

def generate_factor_dashboard(utils, factor_id):
    """Generate a dashboard for a specific factor"""
    try:
        print(f"Generating dashboard for factor ID: {factor_id}...")
        
        # Get factor details
        factor_data = utils.get_factor_details(factor_id)
        
        if factor_data['summary'].empty:
            print(f"No data found for factor ID: {factor_id}")
            return
        
        summary = factor_data['summary']
        details = factor_data['details']
        timeseries = factor_data['timeseries']
        
        # Create output directory
        os.makedirs('factor_dashboard', exist_ok=True)
        
        # Create performance chart if time series data is available
        if not timeseries.empty:
            plt.figure(figsize=(12, 6))
            
            # Calculate cumulative returns
            cumulative_returns = pd.DataFrame(index=timeseries.index)
            
            factor_name = summary['factor_name'].iloc[0]
            
            # Add columns to cumulative returns
            cumulative_returns[f'High_{factor_name}'] = (1 + timeseries['high_portfolio_return']).cumprod()
            cumulative_returns[f'Low_{factor_name}'] = (1 + timeseries['low_portfolio_return']).cumprod()
            cumulative_returns[f'{factor_name}_Factor'] = (1 + timeseries['factor_value']).cumprod()
            
            # Plot cumulative returns
            cumulative_returns.plot(ax=plt.gca())
            plt.title(f'Cumulative Returns of {factor_name} Factor Portfolios')
            plt.xlabel('Date')
            plt.ylabel('Cumulative Return')
            plt.grid(True)
            plt.savefig(f'factor_dashboard/{factor_name.lower()}_cumulative_returns.png')
            
            # Create factor statistics chart
            if not details.empty:
                plt.figure(figsize=(15, 10))
                
                plt.subplot(2, 2, 1)
                sns.histplot(details['beta'], kde=True)
                plt.title('Distribution of Beta Coefficients')
                plt.axvline(x=0, color='r', linestyle='--')
                
                plt.subplot(2, 2, 2)
                sns.histplot(details['tstat'], kde=True)
                plt.title('Distribution of T-statistics')
                plt.axvline(x=1.96, color='r', linestyle='--')
                plt.axvline(x=-1.96, color='r', linestyle='--')
                
                plt.subplot(2, 2, 3)
                sns.histplot(details['rsquared'], kde=True)
                plt.title('Distribution of R-squared Values')
                
                plt.subplot(2, 2, 4)
                rolling_factor = timeseries['factor_value'].rolling(window=min(252, len(timeseries))).mean()
                rolling_factor.plot()
                plt.title(f'Rolling Average of {factor_name} Factor Returns')
                plt.axhline(y=0, color='r', linestyle='--')
                
                plt.tight_layout()
                plt.savefig(f'factor_dashboard/{factor_name.lower()}_factor_statistics.png')
        
        # Create HTML dashboard
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
        """
        
        # Add performance chart if available
        if not timeseries.empty:
            html_content += f"""
            <div class="section">
                <h2>Factor Performance</h2>
                <div class="chart">
                    <img src="{factor_name.lower()}_cumulative_returns.png" width="100%">
                </div>
            </div>
            
            <div class="section">
                <h2>Factor Statistics</h2>
                <div class="chart">
                    <img src="{factor_name.lower()}_factor_statistics.png" width="100%">
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
        
        # Add link back to comparison dashboard
        html_content += """
            <div class="section">
                <p><a href="factor_comparison_dashboard.html">Back to Factor Comparison Dashboard</a></p>
            </div>
        </body>
        </html>
        """
        
        # Write HTML to file
        with open(f'factor_dashboard/{factor_name.lower()}_factor_dashboard.html', 'w') as f:
            f.write(html_content)
        
        print(f"Dashboard created at: factor_dashboard/{factor_name.lower()}_factor_dashboard.html")
    except Exception as e:
        print(f"Error generating factor dashboard: {str(e)}")
        print(traceback.format_exc())

def main():
    """Main function to generate dashboards"""
    try:
        print("Starting dashboard generation...")
        
        # Create utils instance
        utils = ClickHouseUtils()
        
        # Get all factors
        factors = utils.get_all_factors()
        
        if factors.empty:
            print("No factors found in the database")
            return
        
        # Generate individual dashboards
        for _, row in factors.iterrows():
            factor_id = row['factor_id']
            generate_factor_dashboard(utils, factor_id)
        
        # Generate comparison dashboard
        generate_factor_comparison_dashboard(utils)
        
        # Close connection
        utils.close()
        
        print("Dashboard generation complete")
    except Exception as e:
        print(f"Error in main function: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
