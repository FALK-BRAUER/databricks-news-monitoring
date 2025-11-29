# Databricks notebook source
# MAGIC %md
# MAGIC # Job Board RSS Feed Ingestion
# MAGIC
# MAGIC Aggregates CTO/VP job postings from LinkedIn, Indeed, and RemoteOK via RSS feeds
# MAGIC
# MAGIC **Sources:**
# MAGIC - LinkedIn Jobs (public API)
# MAGIC - Indeed RSS
# MAGIC - RemoteOK RSS

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install Dependencies

# COMMAND ----------

%pip install feedparser requests beautifulsoup4 python-dateutil

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup and Configuration

# COMMAND ----------

import json
import hashlib
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, lit, desc
from pyspark.sql.types import *

print("✓ Libraries imported")

# COMMAND ----------

# Load job titles configuration
import json

JOB_TITLES_CONFIG = {
    "executive_tech_roles": [
        "CTO", "Chief Technology Officer", "VP Engineering", "VP of Engineering",
        "Vice President Engineering", "Head of Engineering", "VP Product Engineering",
        "VP Technology", "Chief Architect", "Director of Engineering"
    ],
    "ai_ml_leadership": [
        "VP AI", "VP Machine Learning", "VP AI/ML", "Head of AI",
        "Head of Machine Learning", "Chief AI Officer", "AI Director"
    ],
    "solution_presales": [
        "CTO Solution Advisor", "Solution Architect", "Principal Solution Architect",
        "Solutions Advisor", "Technical Solutions Architect", "Presales Engineer",
        "Presales Solution Architect", "Sales Engineer", "Principal Sales Engineer",
        "Solutions Engineer", "Technical Advisor"
    ],
    "target_locations": {
        "europe": ["Germany", "Switzerland", "Austria", "Berlin", "Munich", "Zurich"],
        "sea": ["Singapore", "Malaysia", "Thailand", "Hong Kong"],
        "remote": ["Remote", "Worldwide"]
    }
}

# Core search queries (title + location combinations)
SEARCH_QUERIES = [
    # CTO roles
    {"title": "CTO", "locations": ["Germany", "Switzerland", "Singapore", "Remote"]},
    {"title": "VP Engineering", "locations": ["Germany", "Switzerland", "Singapore", "Remote"]},
    {"title": "Head of Engineering", "locations": ["Germany", "Switzerland", "Singapore", "Remote"]},
    # AI/ML roles
    {"title": "VP AI", "locations": ["Germany", "Switzerland", "Singapore", "Remote"]},
    # Solution/Presales
    {"title": "Solution Architect", "locations": ["Germany", "Switzerland", "Singapore"]},
    {"title": "Presales Engineer", "locations": ["Germany", "Switzerland", "Singapore"]},
]

CATALOG = 'workspace'
SCHEMA = 'news_monitoring'
TABLE_NAME = 'raw_job_postings'
TABLE_PATH = f"{CATALOG}.{SCHEMA}.{TABLE_NAME}"

print(f"✓ Configuration loaded")
print(f"  Target table: {TABLE_PATH}")
print(f"  Search queries: {len(SEARCH_QUERIES)} title/location combinations")

# COMMAND ----------

# MAGIC %md
# MAGIC ## LinkedIn Jobs Feed Parser

# COMMAND ----------

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

def fetch_linkedin_jobs(title: str, location: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Fetch jobs from LinkedIn public job search API

    Args:
        title: Job title keyword
        location: Location string
        days: Posted within last N days (1, 7, or 30)
    """
    jobs = []

    # LinkedIn uses f_TPR for time posted: r86400 (1d), r604800 (7d), r2592000 (30d)
    time_filters = {1: "r86400", 7: "r604800", 30: "r2592000"}
    f_tpr = time_filters.get(days, "r604800")

    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        "keywords": title,
        "location": location,
        "f_TPR": f_tpr,
        "start": 0
    }

    headers = {"User-Agent": USER_AGENT}

    try:
        print(f"  Fetching LinkedIn: {title} in {location}")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('div', class_='base-card')

        for card in job_cards:
            try:
                title_elem = card.find('h3', class_='base-search-card__title')
                company_elem = card.find('h4', class_='base-search-card__subtitle')
                location_elem = card.find('span', class_='job-search-card__location')
                link_elem = card.find('a', class_='base-card__full-link')

                if not (title_elem and link_elem):
                    continue

                job_url = link_elem.get('href', '').split('?')[0]
                job_id = hashlib.md5(job_url.encode()).hexdigest()

                job = {
                    'job_id': job_id,
                    'source': 'linkedin',
                    'title': title_elem.text.strip() if title_elem else '',
                    'company': company_elem.text.strip() if company_elem else '',
                    'location': location_elem.text.strip() if location_elem else location,
                    'description': '',  # LinkedIn doesn't provide description in list view
                    'url': job_url,
                    'posted_date': None,  # Not available in public API
                    'search_title': title,
                    'search_location': location,
                    'salary': None,
                    'job_type': None,
                    'ingestion_timestamp': datetime.utcnow().isoformat(),
                    'ingestion_date': datetime.utcnow().strftime('%Y-%m-%d')
                }

                jobs.append(job)

            except Exception as e:
                print(f"    Error parsing LinkedIn job card: {str(e)}")
                continue

        print(f"    Found {len(jobs)} jobs")

    except Exception as e:
        print(f"    ERROR fetching LinkedIn: {str(e)}")

    return jobs

# COMMAND ----------

# MAGIC %md
# MAGIC ## Indeed RSS Feed Parser

# COMMAND ----------

def fetch_indeed_jobs(title: str, location: str) -> List[Dict[str, Any]]:
    """
    Fetch jobs from Indeed RSS feed

    Args:
        title: Job title keyword
        location: Location string
    """
    jobs = []

    # Indeed RSS URL pattern
    url = f"https://www.indeed.com/rss?q={title}&l={location}"

    try:
        print(f"  Fetching Indeed: {title} in {location}")
        feed = feedparser.parse(url)

        if not hasattr(feed, 'entries') or not feed.entries:
            print(f"    No entries found")
            return jobs

        for entry in feed.entries:
            try:
                job_url = entry.get('link', '').split('?')[0]
                job_id = hashlib.md5(job_url.encode()).hexdigest()

                # Parse published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_date = datetime(*entry.published_parsed[:6]).isoformat()
                    except:
                        pass

                # Extract description
                description = entry.get('summary', '')
                soup = BeautifulSoup(description, 'html.parser')
                description_text = soup.get_text().strip()

                job = {
                    'job_id': job_id,
                    'source': 'indeed',
                    'title': entry.get('title', ''),
                    'company': '',  # Indeed doesn't always provide company in RSS
                    'location': location,
                    'description': description_text[:1000],  # Truncate
                    'url': job_url,
                    'posted_date': published_date,
                    'search_title': title,
                    'search_location': location,
                    'salary': None,
                    'job_type': None,
                    'ingestion_timestamp': datetime.utcnow().isoformat(),
                    'ingestion_date': datetime.utcnow().strftime('%Y-%m-%d')
                }

                jobs.append(job)

            except Exception as e:
                print(f"    Error parsing Indeed entry: {str(e)}")
                continue

        print(f"    Found {len(jobs)} jobs")

    except Exception as e:
        print(f"    ERROR fetching Indeed: {str(e)}")

    return jobs

# COMMAND ----------

# MAGIC %md
# MAGIC ## RemoteOK RSS Feed Parser

# COMMAND ----------

def fetch_remoteok_jobs(title: str) -> List[Dict[str, Any]]:
    """
    Fetch remote jobs from RemoteOK RSS feed

    Args:
        title: Job title keyword (will be slugified)
    """
    jobs = []

    # RemoteOK uses slugs like "remote-cto-jobs"
    slug = title.lower().replace(' ', '-')
    url = f"https://remoteok.com/remote-{slug}-jobs.rss"

    try:
        print(f"  Fetching RemoteOK: {title}")
        feed = feedparser.parse(url)

        if not hasattr(feed, 'entries') or not feed.entries:
            print(f"    No entries found")
            return jobs

        for entry in feed.entries:
            try:
                job_url = entry.get('link', '')
                job_id = hashlib.md5(job_url.encode()).hexdigest()

                # Parse published date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_date = datetime(*entry.published_parsed[:6]).isoformat()
                    except:
                        pass

                # Extract salary from title or description
                description = entry.get('summary', '')
                salary = None
                if '$' in description:
                    # Simple extraction - can be improved
                    import re
                    salary_match = re.search(r'\$[\d,k-]+', description)
                    if salary_match:
                        salary = salary_match.group()

                job = {
                    'job_id': job_id,
                    'source': 'remoteok',
                    'title': entry.get('title', ''),
                    'company': '',  # Will be in title, needs parsing
                    'location': 'Remote',
                    'description': description[:1000],
                    'url': job_url,
                    'posted_date': published_date,
                    'search_title': title,
                    'search_location': 'Remote',
                    'salary': salary,
                    'job_type': 'Remote',
                    'ingestion_timestamp': datetime.utcnow().isoformat(),
                    'ingestion_date': datetime.utcnow().strftime('%Y-%m-%d')
                }

                jobs.append(job)

            except Exception as e:
                print(f"    Error parsing RemoteOK entry: {str(e)}")
                continue

        print(f"    Found {len(jobs)} jobs")

    except Exception as e:
        print(f"    ERROR fetching RemoteOK: {str(e)}")

    return jobs

# COMMAND ----------

# MAGIC %md
# MAGIC ## Fetch All Jobs

# COMMAND ----------

print("=" * 80)
print("FETCHING JOB POSTINGS FROM ALL SOURCES")
print("=" * 80)

all_jobs = []

# Fetch from each source
for query in SEARCH_QUERIES:
    title = query['title']
    locations = query['locations']

    print(f"\n🔍 Searching for: {title}")

    for location in locations:
        if location == "Remote":
            # Use RemoteOK for remote roles
            jobs = fetch_remoteok_jobs(title)
            all_jobs.extend(jobs)
        else:
            # Use LinkedIn and Indeed for location-specific roles
            linkedin_jobs = fetch_linkedin_jobs(title, location)
            indeed_jobs = fetch_indeed_jobs(title, location)

            all_jobs.extend(linkedin_jobs)
            all_jobs.extend(indeed_jobs)

        # Be nice to servers - add delay
        import time
        time.sleep(2)

print("\n" + "=" * 80)
print(f"SUMMARY: Fetched {len(all_jobs)} total job postings")
print("=" * 80)

# Count by source
by_source = {}
for job in all_jobs:
    source = job['source']
    by_source[source] = by_source.get(source, 0) + 1

print("\nJobs by Source:")
for source, count in sorted(by_source.items()):
    print(f"  {source:20s}: {count:3d} jobs")

print("\n" + "=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Convert to DataFrame

# COMMAND ----------

schema = StructType([
    StructField("job_id", StringType(), False),
    StructField("source", StringType(), False),
    StructField("title", StringType(), True),
    StructField("company", StringType(), True),
    StructField("location", StringType(), True),
    StructField("description", StringType(), True),
    StructField("url", StringType(), True),
    StructField("posted_date", StringType(), True),
    StructField("search_title", StringType(), True),
    StructField("search_location", StringType(), True),
    StructField("salary", StringType(), True),
    StructField("job_type", StringType(), True),
    StructField("ingestion_timestamp", StringType(), False),
    StructField("ingestion_date", StringType(), False)
])

df = spark.createDataFrame(all_jobs, schema=schema)

print(f"✓ Created DataFrame with {df.count()} rows")
print("\nSchema:")
df.printSchema()

print("\nSample data:")
display(df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Delta Lake Table

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
print(f"✓ Schema {CATALOG}.{SCHEMA} ready")

create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_PATH} (
    job_id STRING NOT NULL,
    source STRING NOT NULL,
    title STRING,
    company STRING,
    location STRING,
    description STRING,
    url STRING,
    posted_date STRING,
    search_title STRING,
    search_location STRING,
    salary STRING,
    job_type STRING,
    ingestion_timestamp STRING NOT NULL,
    ingestion_date STRING NOT NULL
)
USING DELTA
PARTITIONED BY (source, ingestion_date)
COMMENT 'Raw job postings from LinkedIn, Indeed, RemoteOK'
"""

spark.sql(create_table_sql)
print(f"✓ Table {TABLE_PATH} ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Delta Lake

# COMMAND ----------

print("Writing to Delta Lake...")

df.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .partitionBy("source", "ingestion_date") \
    .saveAsTable(TABLE_PATH)

print(f"✓ Successfully wrote {df.count()} jobs to {TABLE_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Data

# COMMAND ----------

result_df = spark.table(TABLE_PATH)

print("=" * 80)
print("DATA VERIFICATION")
print("=" * 80)
print(f"\nTotal records in table: {result_df.count()}")

print("\nRecords by source:")
result_df.groupBy("source").count().orderBy("source").show()

print("\nRecords by search title:")
result_df.groupBy("search_title").count().orderBy(desc("count")).show()

print("\nLatest ingestion:")
result_df.filter(col("ingestion_date") == datetime.utcnow().strftime('%Y-%m-%d')) \
    .select("source", "title", "company", "location", "search_title") \
    .show(20, truncate=50)

print("\n" + "=" * 80)
print("INGESTION COMPLETE")
print("=" * 80)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Report

# COMMAND ----------

summary = {
    'run_timestamp': datetime.utcnow().isoformat(),
    'jobs_fetched': len(all_jobs),
    'jobs_written': df.count(),
    'sources': list(by_source.keys()),
    'breakdown_by_source': by_source
}

print("\n" + "=" * 80)
print("JOB INGESTION SUMMARY")
print("=" * 80)
print(json.dumps(summary, indent=2))
print("=" * 80)

print("\n✓ Notebook execution completed successfully")
