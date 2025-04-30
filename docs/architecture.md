# Factor Mining Platform Architecture

## Overview

The Factor Mining Platform is a comprehensive solution for collecting financial data, processing it to discover factors, and visualizing the results. The platform is built on AWS and leverages various services to provide a scalable and reliable solution.

## Architecture Diagram

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Market Data  │     │   SEC Data    │     │  Web Search   │
│    Lambda     │     │    Lambda     │     │    Lambda     │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Clickhouse   │     │      S3       │     │      S3       │
│   Database    │     │    Bucket     │     │    Bucket     │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                     ┌───────────────┐
                     │Step Functions │
                     │  Workflow     │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │   AWS Batch   │
                     │   Processing  │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │  Clickhouse   │
                     │   Database    │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │   Streamlit   │
                     │ Visualization │
                     └───────────────┘
```

## Components

### 1. Data Collection

- **Market Data Lambda**: Collects market data from Yahoo Finance and stores it in Clickhouse
- **SEC Data Lambda**: Collects SEC filings and stores them in S3
- **Web Search Lambda**: Performs web searches and stores results in S3

### 2. Data Storage

- **Clickhouse Database**: Stores market data and factor mining results
- **S3 Buckets**: Store SEC filings and web search results

### 3. Processing

- **Step Functions**: Orchestrates the factor mining workflow
- **AWS Batch**: Executes the factor mining jobs
- **Lambda Functions**: Support the Step Functions workflow

### 4. Visualization

- **Streamlit Application**: Visualizes the factor mining results
- **Application Load Balancer**: Provides access to the Streamlit application

## Data Flow

1. Data collection Lambdas run on a schedule to collect data from various sources
2. The Step Functions workflow is triggered to process the data
3. AWS Batch jobs execute the factor mining algorithms
4. Results are stored in Clickhouse
5. The Streamlit application visualizes the results

## Security

- All components are deployed in a VPC with appropriate security groups
- IAM roles follow the principle of least privilege
- Data is encrypted at rest and in transit

## Scalability

- AWS Batch can scale to handle large workloads
- Clickhouse can be scaled by increasing instance size or adding replicas
- The architecture supports horizontal scaling of all components
