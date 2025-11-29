# Databricks News Monitoring

A comprehensive Databricks-based platform for monitoring and analyzing news about startups, scaleups, PE/VC activity, and job market trends.

## Overview

This project provides automated data pipelines to:
- Collect news from multiple sources (APIs, RSS feeds, web scraping)
- Monitor startup and scaleup company news
- Track Private Equity and Venture Capital activity
- Analyze job market trends in the startup ecosystem
- Store and process data using Delta Lake
- Generate insights and reports

## Project Structure

```
databricks-news-monitoring/
├── notebooks/               # Databricks notebooks
│   ├── ingestion/          # Data ingestion notebooks
│   ├── transformation/     # Data transformation logic
│   └── analysis/           # Analysis and reporting
├── src/                    # Python source code
│   ├── utils/              # Utility functions
│   └── data_sources/       # Data source connectors
├── config/                 # Configuration files
│   └── config.yaml         # Main configuration
├── tests/                  # Unit tests
├── data/                   # Local data (gitignored)
│   ├── raw/                # Raw data
│   └── processed/          # Processed data
├── databricks.yml          # Databricks Asset Bundle config
└── requirements.txt        # Python dependencies
```

## Prerequisites

- Databricks workspace (AWS/Azure/GCP)
- AWS account with:
  - S3 bucket for data storage
  - Secrets Manager for API keys
- Python 3.9+
- Databricks CLI

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/FALK-BRAUER/databricks-news-monitoring.git
cd databricks-news-monitoring
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

Ensure your AWS credentials are configured:

```bash
aws configure
```

### 4. Set Up Databricks

Install Databricks CLI:

```bash
databricks configure
```

### 5. Configure Secrets

API keys and credentials are stored in AWS Secrets Manager (ap-southeast-1):
- Secret name: `AWS`
- Keys: `GITHUB`, `CLAUDE`, `GEMINI`, etc.

### 6. Deploy to Databricks

Using Databricks Asset Bundles:

```bash
# Validate the bundle
databricks bundle validate

# Deploy to development
databricks bundle deploy -t dev

# Deploy to production
databricks bundle deploy -t prod
```

## Configuration

Edit `config/config.yaml` to customize:

- **Data sources**: Enable/disable news APIs, RSS feeds, job boards
- **AWS settings**: S3 bucket, region, secrets
- **Delta tables**: Catalog, schema, table names
- **Processing**: Batch size, lookback period, deduplication

## Data Sources

### News APIs
- NewsAPI
- GNews
- RSS Feeds (TechCrunch, PitchBook)

### Job Boards
- LinkedIn (planned)
- AngelList (planned)

### Company Databases
- Crunchbase (planned)
- PitchBook (planned)

## Delta Lake Schema

### Tables

1. **raw_news_articles**: Raw news data from all sources
2. **processed_news_articles**: Cleaned and enriched news articles
3. **vc_pe_deals**: Venture capital and private equity deals
4. **job_postings**: Job market data

## Workflows

### Daily News Ingestion

Runs daily at 2:00 AM UTC:

1. Ingest startup news
2. Ingest VC/PE news
3. Ingest job market data

Configured in `databricks.yml`

## Development

### Local Testing

```bash
# Run tests
pytest tests/

# Code formatting
black src/ notebooks/

# Linting
flake8 src/
```

### Adding New Data Sources

1. Create a new module in `src/data_sources/`
2. Implement the connector class
3. Add configuration to `config/config.yaml`
4. Create corresponding notebook in `notebooks/ingestion/`

## Monitoring & Alerts

- Email alerts: falk.brauer@me.com
- Slack webhooks: (to be configured)
- Databricks job notifications

## Security

- **Never commit secrets**: All credentials in AWS Secrets Manager
- **Use IAM roles**: For Databricks cluster access to AWS
- **Network security**: Configure VPC and security groups appropriately

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

Private repository - All rights reserved

## Contact

**Falk Brauer**
- Email: falk.brauer@me.com
- GitHub: [@FALK-BRAUER](https://github.com/FALK-BRAUER)

## Roadmap

- [ ] Implement RSS feed ingestion
- [ ] Add NewsAPI integration
- [ ] Integrate LinkedIn job scraping
- [ ] Add Crunchbase API connector
- [ ] Build analysis dashboards
- [ ] Implement real-time streaming
- [ ] Add NLP sentiment analysis
- [ ] Create automated reporting
