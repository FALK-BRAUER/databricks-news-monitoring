# 📰 News Monitoring & Startup Intelligence Platform

An automated data pipeline for monitoring startup news, funding rounds, acquisitions, and job market trends across Southeast Asia, Europe, and global markets.

## 🎯 What This Does

Automatically collects, enriches, and analyzes news from multiple sources to track:
- 💰 Funding rounds (Seed, Series A/B/C, etc.)
- 🤝 Acquisitions and M&A activity  
- 📈 Startup activity by region
- 💼 Hiring and layoff trends
- 🏢 Company mentions and trending startups

## 🏗️ Architecture

### Medallion Architecture (Bronze → Silver → Gold)

```
RSS Feeds (4 sources)
    ↓
📊 BRONZE: Raw news articles
    ↓ (Entity Extraction & Categorization)
🔧 SILVER: Enriched articles with extracted entities
    ↓ (Aggregation & Analytics)
💎 GOLD: Analytics-ready business views
    ↓
📈 Dashboards & Alerts
```

## 📊 Current Status

✅ **Production Ready**

- Bronze layer collecting ~100 articles/day
- Silver layer extracting entities and categorizing
- Gold layer with 5 analytics tables
- Complete ETL pipeline running daily at 3:00 AM UTC
- 12 pre-built SQL queries for dashboards

## 🚀 Quick Start

View your data in Databricks SQL:

```sql
-- Recent funding rounds
SELECT title, funding_round, funding_amount_millions, region
FROM workspace.news_monitoring.gold_funding_tracker
ORDER BY published_date DESC
LIMIT 10;

-- Regional overview
SELECT * FROM workspace.news_monitoring.gold_regional_trends;
```

See `sql/dashboard_queries.sql` for all 12 queries.

## 📈 Dashboard

Access pre-built queries in `sql/dashboard_queries.sql` for:
- Regional activity overview
- Recent funding rounds
- Top mentioned companies
- Category analysis
- Hiring vs layoffs trends

## 🔧 Workflows

**Complete ETL Pipeline (Active)**
- Job ID: 82343254902219
- Schedule: Daily at 3:00 AM UTC
- URL: https://dbc-5a365369-15d1.cloud.databricks.com/#job/82343254902219

**Tasks:**
1. Bronze: Ingest RSS feeds
2. Silver: Extract entities & categorize
3. Gold: Create analytics tables

## 📊 Data Tables

All tables in `workspace.news_monitoring`:

**Bronze:**
- `raw_news_articles` - Raw RSS data

**Silver:**
- `silver_articles` - Enriched articles with entities

**Gold:**
- `gold_daily_activity` - Daily metrics
- `gold_funding_tracker` - Funding announcements
- `gold_regional_trends` - Regional stats
- `gold_company_mentions` - Company tracking
- `gold_category_analysis` - Category breakdown

## 📧 Alerts

Email notifications to falk.brauer@me.com on workflow failures.

---

For full documentation, see `README_OLD.md` or check `WORKFLOW_MANAGEMENT.md`
