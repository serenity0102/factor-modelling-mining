#!/bin/bash

# Set environment variables
export CLICKHOUSE_HOST=44.222.122.134
export CLICKHOUSE_PORT=9000
export CLICKHOUSE_USER=default
export CLICKHOUSE_PASSWORD='clickhouse@aws'
export CLICKHOUSE_DATABASE=factor_model_tick_data_database
export AWS_REGION=us-east-1
export STATE_MACHINE_ARN=arn:aws:states:us-east-1:600627331406:stateMachine:factor-modeling-workflow

# Set AWS profile
export AWS_PROFILE=factor

# Run the Streamlit application
streamlit run app.py
