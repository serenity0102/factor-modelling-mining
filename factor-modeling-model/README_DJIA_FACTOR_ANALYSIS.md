# DJIA 30 Factor Modeling Analysis

This project implements factor modeling for the DJIA 30 stocks, analyzing the effectiveness of various factors including PEG, RSI, and Fama-French factors (SMB, HML, Rm-Rf).

## Overview

The analysis follows these steps for each factor (using PEG as an example):

1. **Sorting and Grouping**: Sort the 30 DJIA stocks by PEG from high to low.
2. **Portfolio Construction**:
   - High PEG Portfolio: Market-cap weighted portfolio of high PEG stocks
   - Low PEG Portfolio: Market-cap weighted portfolio of low PEG stocks
3. **Factor Calculation**: PEG Factor = Return High PEG − Return Low PEG
4. **Factor Testing**:
   - Regression model: Ri = α + β⋅PEG Factor + ϵi
   - Significance testing: |T-stat| > 1.96 indicates significant factor
   - R-squared analysis: Measures factor's explanatory power
   - Backtesting: Performance of long-short portfolio based on factor

## Data Source

The analysis uses stock price data from a ClickHouse database:
- Host: 44.222.122.134:9000
- Database: jacky_database1
- Table: tick_data
- User: jacky_user

For fundamental data (P/E ratios, growth rates), we generate synthetic data based on price patterns.

## Project Structure

- `djia_factor_analysis.py` - Core implementation of factor analysis
- `run_djia_factor_analysis.py` - Script to run analysis and store results
- `clickhouse_utils.py` - Utility functions for ClickHouse operations
- `generate_factor_dashboard.py` - Dashboard generation script
- `requirements.txt` - Required Python packages

## Getting Started

### Installation

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Analysis

To run the factor analysis:

```bash
python run_djia_factor_analysis.py
```

This will:
1. Fetch stock data from the ClickHouse database
2. Generate necessary fundamental data
3. Run the PEG factor analysis
4. Store results in the ClickHouse database
5. Generate visualizations and a dashboard

To generate dashboards from existing data:

```bash
python generate_factor_dashboard.py
```

## Results

The analysis produces several outputs:

1. **ClickHouse Database**: Results stored in tables:
   - `factor_summary` - Summary statistics for each factor
   - `factor_details` - Detailed stock-level results for each factor
   - `factor_timeseries` - Time series data for factor values

2. **Visualizations**:
   - Cumulative returns charts
   - Statistical analysis charts
   - Factor comparison charts

3. **Dashboard**:
   - Individual factor dashboards
   - Factor comparison dashboard

## Interpreting Results

- **T-statistic**: |T-stat| > 1.96 indicates the factor has a statistically significant effect
- **R-squared**: Higher values indicate better explanatory power
- **Sharpe Ratio**: Higher values indicate better risk-adjusted returns
- **Confidence Intervals**: Narrower intervals indicate more precise estimates

## Future Enhancements

1. Add implementation for RSI factor
2. Add implementation for Fama-French factors
3. Implement regime analysis to test factor performance in different market conditions
4. Add machine learning models to predict factor performance

## License

This project is licensed under the MIT License - see the LICENSE file for details.
