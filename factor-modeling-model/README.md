# DJIA Factor Modeling Analysis

This project implements factor modeling for the DJIA 30 stocks, analyzing the effectiveness of various factors including PEG, RSI-14, RSI-28, and more.

## Overview

The analysis follows these steps for each factor:

1. **Sorting and Grouping**: Sort the 30 DJIA stocks by factor value
2. **Portfolio Construction**:
   - High Factor Portfolio: Market-cap weighted portfolio of high factor stocks
   - Low Factor Portfolio: Market-cap weighted portfolio of low factor stocks
3. **Factor Calculation**: Factor Return = Return High Portfolio − Return Low Portfolio
4. **Factor Testing**:
   - Regression model: Ri = α + β⋅Factor + ϵi
   - Significance testing: |T-stat| > 1.96 indicates significant factor
   - R-squared analysis: Measures factor's explanatory power
   - Backtesting: Performance of long-short portfolio based on factor

## Implemented Factors

### Fundamental Factors
- **PEG (Price/Earnings to Growth)**: Lower PEG indicates better value relative to growth

### Technical Factors
- **RSI-14 (Relative Strength Index, 14-day window)**: Measures momentum by comparing recent gains to recent losses
- **RSI-28 (Relative Strength Index, 28-day window)**: Longer-term momentum indicator with less sensitivity to short-term price changes

## Data Source

The analysis uses stock price data from a ClickHouse database:
- Host: 44.222.122.134:9000
- Database: jacky_database1
- Table: tick_data
- User: jacky_user

## Project Structure

- `djia_factor_analysis.py` - Core implementation of factor analysis
- `clickhouse_utils.py` - Utility functions for ClickHouse operations
- `run_factor_analysis.py` - Script to run analysis for multiple factors
- `generate_factor_dashboard.py` - Dashboard generation script
- `requirements.txt` - Required Python packages

## Database Schema

The project uses the following tables in ClickHouse:

1. **factor_summary** - Summary statistics for each factor
   - factor_name, factor_type, test_date, etc.
   - Performance metrics: annualized_return, sharpe_ratio, etc.
   - update_time: DateTime for tracking record creation

2. **factor_details** - Detailed stock-level results for each factor
   - factor_name, factor_type, test_date, ticker, beta, tstat, etc.

3. **factor_timeseries** - Time series data for factor values
   - factor_name, factor_type, date, factor_value, etc.

4. **factor_values** - Raw factor values for each stock
   - factor_type, factor_name, ticker, date, value

## Getting Started

### Installation

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

### Running the Analysis

To run the factor analysis for all factors:

```bash
python run_factor_analysis.py --all
```

To run the analysis for a specific factor:

```bash
python run_factor_analysis.py --factor PEG
python run_factor_analysis.py --factor RSI14
python run_factor_analysis.py --factor RSI28
```

To specify a date range:

```bash
python run_factor_analysis.py --all --start-date 2025-01-01 --end-date 2025-03-31
```

### Generating Dashboards

To generate dashboards from the stored factor data:

```bash
python generate_factor_dashboard.py
```

## Results

The analysis produces several outputs:

1. **ClickHouse Database**: Results stored in tables
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

## Adding New Factors

To add a new factor:

1. Implement the factor calculation function in `djia_factor_analysis.py`
2. Create a factor analysis function similar to `run_peg_factor_analysis` or `run_rsi_factor_analysis`
3. Add the factor to `run_factor_analysis.py`
4. Run the analysis and generate dashboards

## License

This project is licensed under the MIT License - see the LICENSE file for details.
