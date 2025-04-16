## ClickHouse Table Schema    
    CREATE TABLE stock_fundamental_factors_source
    (
        -- Basic identifiers
        ticker String,                           -- Stock ticker symbol (e.g., AAPL, MSFT)
        cik String,                              -- SEC Central Index Key identifier with leading zeros (e.g., 0000320193)
        end_date Date,                        -- Date of the financial report/statement (format: YYYY-MM-DD)
        filed_date Date,                        -- Date when the report was filed with SEC (format: YYYY-MM-DD)
        form Enum('10-K' = 1, '10-Q' = 2), -- Type of filing: 10-K (annual) or 10-Q (quarterly)
        fiscal_year UInt16,                      -- Fiscal year of the report (e.g., 2024)
        fiscal_quarter String,                    -- Fiscal quarter (Q1, Q2, Q3, Q4)
        
        -- Balance sheet metrics
        assets_current Decimal(20, 2),           -- Current assets in USD
        liabilities_current Decimal(20, 2),      -- Current liabilities in USD
        cash_and_equivalents Decimal(20, 2),     -- Cash and cash equivalents at carrying value in USD
        inventory_net Decimal(20, 2),            -- Net inventory in USD for current period
        inventory_net_prev_year Decimal(20, 2),  -- Net inventory in USD from previous year
        stockholders_equity Decimal(20, 2),      -- Total stockholders equity in USD
        
        -- Income statement metrics
        sales_revenue_net Decimal(20, 2),        -- Net sales revenue in USD for current period
        sales_revenue_net_prev_year Decimal(20, 2), -- Net sales revenue in USD from previous year
        cost_of_goods_sold Decimal(20, 2),       -- Cost of goods and services sold in USD
        interest_expense Decimal(20, 2),         -- Interest expense in USD
        income_before_taxes Decimal(20, 2),      -- Income before taxes, minority interest, and equity method investments in USD
        
        -- Metadata fields
        source_file String,                      -- Source file path or identifier (e.g., S3 path)
        processed_timestamp DateTime DEFAULT now(), -- Timestamp when the record was processed
        create_datetime DateTime DEFAULT now()   -- Timestamp when the record was created in the database
    )
    ENGINE = MergeTree()
    ORDER BY (ticker, end_date, filed_date)
    PARTITION BY toYYYYMM(end_date);