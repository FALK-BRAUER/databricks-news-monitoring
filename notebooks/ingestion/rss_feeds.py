# Databricks notebook source
# MAGIC %md
# MAGIC # RSS Feed Ingestion
# MAGIC
# MAGIC This notebook fetches news articles from RSS feeds and stores them in Delta Lake.
# MAGIC
# MAGIC **Data Sources:**
# MAGIC - TechCrunch (Global startup news)
# MAGIC - Tech.eu (Europe: Germany, Switzerland)
# MAGIC - Tech in Asia (Southeast Asia)
# MAGIC - Crunchbase News (VC/PE deals)
# MAGIC
# MAGIC **Target Regions:** SEA, Australia, Hong Kong, Germany, Switzerland
# MAGIC
# MAGIC **Schedule:** Daily at 2:00 AM UTC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Configuration

# COMMAND ----------

# Import required libraries
import sys
import json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit
from pyspark.sql.types import *
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("✓ Libraries imported")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install Dependencies

# COMMAND ----------

# Install required packages
%pip install feedparser python-dateutil --quiet

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Configuration

# COMMAND ----------

# Configuration
CONFIG = {
    'data_sources': {
        'news_apis': [
            {
                'name': 'rss_feeds',
                'enabled': True,
                'feeds': [
                    {
                        'url': 'https://techcrunch.com/feed/',
                        'name': 'techcrunch',
                        'category': 'startup',
                        'region': 'global',
                        'countries': [],
                        'requires_user_agent': False
                    },
                    {
                        'url': 'https://news.crunchbase.com/feed/',
                        'name': 'crunchbase_news',
                        'category': 'vc-pe',
                        'region': 'global',
                        'countries': [],
                        'requires_user_agent': False
                    },
                    {
                        'url': 'https://tech.eu/feed/',
                        'name': 'tech_eu',
                        'category': 'startup',
                        'region': 'europe',
                        'countries': ['DE', 'CH', 'AT', 'EU'],
                        'requires_user_agent': False
                    },
                    {
                        'url': 'https://www.techinasia.com/feed',
                        'name': 'tech_in_asia',
                        'category': 'startup',
                        'region': 'sea',
                        'countries': ['SG', 'MY', 'ID', 'TH', 'VN', 'PH'],
                        'requires_user_agent': True
                    }
                ]
            }
        ]
    }
}

# Delta Lake table configuration
CATALOG = 'main'
SCHEMA = 'news_monitoring'
TABLE_NAME = 'raw_news_articles'
TABLE_PATH = f"{CATALOG}.{SCHEMA}.{TABLE_NAME}"

print(f"✓ Configuration loaded")
print(f"  Target table: {TABLE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## RSS Parser Functions

# COMMAND ----------

import feedparser
import requests
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

# Browser User-Agent for feeds that require it
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

def fetch_feed(url: str, requires_user_agent: bool = False, timeout: int = 30):
    """Fetch and parse an RSS feed."""
    try:
        if requires_user_agent:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
        else:
            feed = feedparser.parse(url)

        return feed
    except Exception as e:
        logger.error(f"Failed to fetch feed {url}: {str(e)}")
        raise

def parse_entry(entry, source_name: str, region: str = "global", countries: List[str] = None):
    """Parse a single RSS feed entry."""
    # Generate unique article ID from URL
    article_url = entry.get('link', '')
    article_id = hashlib.md5(article_url.encode()).hexdigest()

    # Parse publication date
    published_date = None
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            published_date = datetime(*entry.published_parsed[:6]).isoformat()
        except (TypeError, ValueError):
            pass

    if not published_date and hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        try:
            published_date = datetime(*entry.updated_parsed[:6]).isoformat()
        except (TypeError, ValueError):
            pass

    # Extract categories/tags
    categories = []
    if hasattr(entry, 'tags'):
        categories = [tag.get('term', '') for tag in entry.tags if tag.get('term')]

    # Extract author
    author = entry.get('author', '')
    if not author and hasattr(entry, 'authors') and entry.authors:
        author = entry.authors[0].get('name', '')

    # Extract content
    content = ''
    if hasattr(entry, 'content') and entry.content:
        content = entry.content[0].get('value', '')
    elif hasattr(entry, 'summary_detail'):
        content = entry.summary_detail.get('value', '')

    # Build structured article
    article = {
        'article_id': article_id,
        'source': source_name,
        'title': entry.get('title', ''),
        'description': entry.get('summary', ''),
        'content': content,
        'url': article_url,
        'author': author,
        'published_date': published_date,
        'categories': categories,
        'region': region,
        'country_codes': countries or [],
        'ingestion_timestamp': datetime.utcnow().isoformat(),
        'ingestion_date': datetime.utcnow().strftime('%Y-%m-%d')
    }

    return article

def fetch_all_feeds(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Fetch articles from all configured RSS feeds."""
    all_articles = []

    rss_config = config.get('data_sources', {}).get('news_apis', [])
    rss_feeds = None

    for source in rss_config:
        if source.get('name') == 'rss_feeds' and source.get('enabled'):
            rss_feeds = source.get('feeds', [])
            break

    if not rss_feeds:
        logger.warning("No RSS feeds configured")
        return []

    for feed_config in rss_feeds:
        url = feed_config.get('url')
        name = feed_config.get('name', 'unknown')
        region = feed_config.get('region', 'global')
        countries = feed_config.get('countries', [])
        requires_ua = feed_config.get('requires_user_agent', False)

        if not url:
            logger.warning(f"Missing URL for feed: {name}")
            continue

        logger.info(f"Fetching feed: {name} ({url})")

        try:
            feed = fetch_feed(url, requires_ua)

            if not hasattr(feed, 'entries') or not feed.entries:
                logger.warning(f"No entries found in feed: {name}")
                continue

            for entry in feed.entries:
                try:
                    article = parse_entry(entry, name, region, countries)
                    all_articles.append(article)
                except Exception as e:
                    logger.error(f"Error parsing entry from {name}: {str(e)}")
                    continue

            logger.info(f"✓ Parsed {len([a for a in all_articles if a['source'] == name])} articles from {name}")

        except Exception as e:
            logger.error(f"Failed to parse feed {name}: {str(e)}")
            continue

    logger.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles

print("✓ RSS parser functions defined")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Fetch RSS Feeds

# COMMAND ----------

print("=" * 80)
print("FETCHING RSS FEEDS")
print("=" * 80)

# Fetch articles from all feeds
articles = fetch_all_feeds(CONFIG)

# Display summary
print("\n" + "=" * 80)
print(f"SUMMARY: Fetched {len(articles)} articles")
print("=" * 80)

# Group by source
by_source = {}
by_region = {}

for article in articles:
    source = article['source']
    region = article['region']

    by_source[source] = by_source.get(source, 0) + 1
    by_region[region] = by_region.get(region, 0) + 1

print("\nArticles by Source:")
for source, count in sorted(by_source.items()):
    print(f"  {source:20s}: {count:3d} articles")

print("\nArticles by Region:")
for region, count in sorted(by_region.items()):
    print(f"  {region:20s}: {count:3d} articles")

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Convert to DataFrame

# COMMAND ----------

# Define schema for Delta Lake table
schema = StructType([
    StructField("article_id", StringType(), False),
    StructField("source", StringType(), False),
    StructField("title", StringType(), True),
    StructField("description", StringType(), True),
    StructField("content", StringType(), True),
    StructField("url", StringType(), True),
    StructField("author", StringType(), True),
    StructField("published_date", StringType(), True),
    StructField("categories", ArrayType(StringType()), True),
    StructField("region", StringType(), True),
    StructField("country_codes", ArrayType(StringType()), True),
    StructField("ingestion_timestamp", StringType(), False),
    StructField("ingestion_date", StringType(), False)
])

# Convert to Spark DataFrame
df = spark.createDataFrame(articles, schema=schema)

print(f"✓ Created DataFrame with {df.count()} rows")
print("\nSchema:")
df.printSchema()

print("\nSample data:")
display(df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Delta Lake Table (First Run Only)

# COMMAND ----------

# Create schema if it doesn't exist
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
print(f"✓ Schema {CATALOG}.{SCHEMA} ready")

# Create table if it doesn't exist
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_PATH} (
    article_id STRING NOT NULL,
    source STRING NOT NULL,
    title STRING,
    description STRING,
    content STRING,
    url STRING,
    author STRING,
    published_date STRING,
    categories ARRAY<STRING>,
    region STRING,
    country_codes ARRAY<STRING>,
    ingestion_timestamp STRING NOT NULL,
    ingestion_date STRING NOT NULL
)
USING DELTA
PARTITIONED BY (source, ingestion_date)
COMMENT 'Raw news articles from RSS feeds'
"""

spark.sql(create_table_sql)
print(f"✓ Table {TABLE_PATH} ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Delta Lake

# COMMAND ----------

print("Writing to Delta Lake...")

# Write to Delta table (append mode)
df.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .partitionBy("source", "ingestion_date") \
    .saveAsTable(TABLE_PATH)

print(f"✓ Successfully wrote {df.count()} articles to {TABLE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Data

# COMMAND ----------

# Read from Delta table to verify
result_df = spark.table(TABLE_PATH)

print("=" * 80)
print("DATA VERIFICATION")
print("=" * 80)
print(f"\nTotal records in table: {result_df.count()}")

# Show records by source
print("\nRecords by source:")
result_df.groupBy("source").count().orderBy("source").show()

# Show records by region
print("\nRecords by region:")
result_df.groupBy("region").count().orderBy("region").show()

# Show latest ingestion
print("\nLatest ingestion:")
result_df.filter(col("ingestion_date") == datetime.utcnow().strftime('%Y-%m-%d')) \
    .select("source", "title", "published_date", "region") \
    .show(10, truncate=50)

print("\n" + "=" * 80)
print("INGESTION COMPLETE")
print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Report

# COMMAND ----------

# Generate summary report
summary = {
    'run_timestamp': datetime.utcnow().isoformat(),
    'articles_fetched': len(articles),
    'articles_written': df.count(),
    'sources': list(by_source.keys()),
    'regions': list(by_region.keys()),
    'breakdown_by_source': by_source,
    'breakdown_by_region': by_region
}

print("\n" + "=" * 80)
print("INGESTION SUMMARY")
print("=" * 80)
print(json.dumps(summary, indent=2))
print("=" * 80)

# Return summary for workflow monitoring
dbutils.notebook.exit(json.dumps(summary))
