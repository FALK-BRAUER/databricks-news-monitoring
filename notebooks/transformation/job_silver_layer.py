# Databricks notebook source
# MAGIC %md
# MAGIC # Job Postings Silver Layer
# MAGIC
# MAGIC Transforms raw job postings with:
# MAGIC - Deduplication across sources
# MAGIC - Job categorization (Executive, AI/ML, Solution/Presales)
# MAGIC - Seniority level extraction
# MAGIC - Company name extraction
# MAGIC - Location standardization

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
from datetime import datetime
import re

print("✓ Libraries imported")

# COMMAND ----------

CATALOG = 'workspace'
SCHEMA = 'news_monitoring'
SOURCE_TABLE = f"{CATALOG}.{SCHEMA}.raw_job_postings"
TARGET_TABLE = f"{CATALOG}.{SCHEMA}.silver_job_postings"

print(f"Source: {SOURCE_TABLE}")
print(f"Target: {TARGET_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Raw Data

# COMMAND ----------

raw_df = spark.table(SOURCE_TABLE)

print(f"✓ Loaded {raw_df.count()} raw job postings")
print(f"  Date range: {raw_df.agg(min('ingestion_date'), max('ingestion_date')).collect()[0]}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Categorize Jobs

# COMMAND ----------

# UDF to categorize job type
@udf(returnType=ArrayType(StringType()))
def categorize_job(title, description):
    """Categorize job into executive_tech, ai_ml, solution_presales"""
    if not title:
        return []

    title_lower = title.lower()
    desc_lower = (description or "").lower()
    combined = f"{title_lower} {desc_lower}"

    categories = []

    # Executive Tech
    exec_keywords = ['cto', 'chief technology', 'vp engineering', 'vice president engineering',
                     'head of engineering', 'vp product', 'director of engineering']
    if any(kw in title_lower for kw in exec_keywords):
        categories.append('executive_tech')

    # AI/ML Leadership
    ai_keywords = ['vp ai', 'vp ml', 'head of ai', 'head of ml', 'chief ai',
                   'ai director', 'ml director', 'machine learning']
    if any(kw in combined for kw in ai_keywords):
        categories.append('ai_ml')

    # Solution/Presales
    solution_keywords = ['solution architect', 'solutions architect', 'presales',
                        'sales engineer', 'solutions engineer', 'technical advisor']
    if any(kw in combined for kw in solution_keywords):
        categories.append('solution_presales')

    return categories if categories else ['other']

# COMMAND ----------

# UDF to extract seniority level
@udf(returnType=StringType())
def extract_seniority(title):
    """Extract seniority level from title"""
    if not title:
        return 'unknown'

    title_lower = title.lower()

    # C-level
    if any(word in title_lower for word in ['cto', 'chief', 'c-level']):
        return 'c_level'

    # VP level
    if any(word in title_lower for word in ['vp', 'vice president', 'v.p.']):
        return 'vp'

    # Head/Director
    if any(word in title_lower for word in ['head of', 'director']):
        return 'director'

    # Principal/Lead
    if any(word in title_lower for word in ['principal', 'lead', 'staff']):
        return 'principal'

    # Senior
    if 'senior' in title_lower or 'sr.' in title_lower:
        return 'senior'

    return 'mid_level'

# COMMAND ----------

# UDF to standardize location to region
@udf(returnType=StringType())
def standardize_region(location):
    """Map location to region"""
    if not location:
        return 'unknown'

    loc_lower = location.lower()

    # Remote
    if any(word in loc_lower for word in ['remote', 'worldwide', 'global', 'anywhere']):
        return 'remote'

    # Europe
    europe_countries = ['germany', 'switzerland', 'austria', 'berlin', 'munich',
                       'zurich', 'vienna', 'hamburg', 'frankfurt']
    if any(country in loc_lower for country in europe_countries):
        return 'europe'

    # SEA
    sea_countries = ['singapore', 'malaysia', 'indonesia', 'thailand', 'vietnam',
                    'philippines', 'hong kong', 'bangkok', 'jakarta', 'kuala lumpur']
    if any(country in loc_lower for country in sea_countries):
        return 'sea'

    # US
    if any(word in loc_lower for word in ['united states', 'usa', 'us,', 'san francisco',
                                           'new york', 'boston', 'seattle', 'austin']):
        return 'us'

    return 'other'

# COMMAND ----------

# UDF to extract salary range
@udf(returnType=StringType())
def extract_salary(description, salary_field):
    """Extract salary information"""
    text = f"{description or ''} {salary_field or ''}"

    if not text.strip():
        return None

    # Look for common salary patterns
    # $100k-$150k, $100,000-$150,000, €80k-€120k
    patterns = [
        r'[\$€£]\s*(\d{1,3}[,k]?\d{0,3})\s*-\s*[\$€£]?\s*(\d{1,3}[,k]?\d{0,3})',
        r'(\d{1,3}[,k]?\d{0,3})\s*-\s*(\d{1,3}[,k]?\d{0,3})\s*[\$€£]',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)

    return None

# COMMAND ----------

# MAGIC %md
# MAGIC ## Transform Data

# COMMAND ----------

# Apply transformations
transformed_df = raw_df \
    .withColumn("job_categories", categorize_job(col("title"), col("description"))) \
    .withColumn("seniority_level", extract_seniority(col("title"))) \
    .withColumn("region", standardize_region(col("location"))) \
    .withColumn("salary_range", extract_salary(col("description"), col("salary"))) \
    .withColumn("is_remote",
                when(lower(col("location")).contains("remote"), True)
                .when(col("region") == "remote", True)
                .otherwise(False)) \
    .withColumn("processing_timestamp", current_timestamp())

print(f"✓ Applied transformations")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Deduplicate

# COMMAND ----------

# Deduplicate by URL, keeping the most recent ingestion
# Also deduplicate by title+company for jobs from different sources

window_spec = Window.partitionBy("url").orderBy(desc("ingestion_timestamp"))

deduped_df = transformed_df \
    .withColumn("row_num", row_number().over(window_spec)) \
    .filter(col("row_num") == 1) \
    .drop("row_num")

original_count = transformed_df.count()
deduped_count = deduped_df.count()
duplicates_removed = original_count - deduped_count

print(f"✓ Deduplication complete")
print(f"  Original: {original_count} jobs")
print(f"  Deduplicated: {deduped_count} jobs")
print(f"  Removed: {duplicates_removed} duplicates")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Add Relevance Score

# COMMAND ----------

# Calculate base relevance score (0-100)
relevance_df = deduped_df \
    .withColumn("relevance_score",
        when(col("seniority_level") == "c_level", lit(100))
        .when(col("seniority_level") == "vp", lit(90))
        .when(col("seniority_level") == "director", lit(75))
        .when(col("seniority_level") == "principal", lit(60))
        .when(col("seniority_level") == "senior", lit(40))
        .otherwise(lit(20))
    ) \
    .withColumn("relevance_score",
        # Boost for target regions
        when(col("region").isin(["europe", "sea", "remote"]), col("relevance_score") + 10)
        .otherwise(col("relevance_score"))
    ) \
    .withColumn("relevance_score",
        # Boost for multiple categories
        when(size(col("job_categories")) > 1, col("relevance_score") + 5)
        .otherwise(col("relevance_score"))
    )

print(f"✓ Added relevance scores")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Silver Table

# COMMAND ----------

create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TARGET_TABLE} (
    job_id STRING NOT NULL,
    source STRING NOT NULL,
    title STRING,
    company STRING,
    location STRING,
    region STRING,
    description STRING,
    url STRING,
    posted_date STRING,
    search_title STRING,
    search_location STRING,
    salary STRING,
    salary_range STRING,
    job_type STRING,
    is_remote BOOLEAN,
    job_categories ARRAY<STRING>,
    seniority_level STRING,
    relevance_score INT,
    ingestion_timestamp STRING NOT NULL,
    ingestion_date STRING NOT NULL,
    processing_timestamp TIMESTAMP NOT NULL
)
USING DELTA
PARTITIONED BY (ingestion_date, region)
COMMENT 'Enriched and deduplicated job postings'
"""

spark.sql(create_table_sql)
print(f"✓ Table {TARGET_TABLE} ready")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Silver Table

# COMMAND ----------

print("Writing to silver table...")

relevance_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .option("overwriteSchema", "true") \
    .partitionBy("ingestion_date", "region") \
    .saveAsTable(TARGET_TABLE)

print(f"✓ Wrote {deduped_count} jobs to {TARGET_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verification

# COMMAND ----------

result_df = spark.table(TARGET_TABLE)

print("=" * 80)
print("SILVER LAYER VERIFICATION")
print("=" * 80)
print(f"\nTotal jobs: {result_df.count()}")

print("\nBy Region:")
result_df.groupBy("region").count().orderBy(desc("count")).show()

print("\nBy Seniority Level:")
result_df.groupBy("seniority_level").count().orderBy(desc("count")).show()

print("\nBy Job Category:")
result_df.select(explode("job_categories").alias("category")).groupBy("category").count().orderBy(desc("count")).show()

print("\nTop Relevance Scores:")
result_df.select("title", "seniority_level", "region", "relevance_score") \
    .orderBy(desc("relevance_score")) \
    .show(10, truncate=50)

print("\n" + "=" * 80)
print("SILVER LAYER PROCESSING COMPLETE")
print("=" * 80)

# COMMAND ----------

# Summary (avoiding RDD for serverless compatibility)
import json

regions_list = [row.region for row in result_df.select("region").distinct().collect()]
seniority_list = [row.seniority_level for row in result_df.select("seniority_level").distinct().collect()]

summary = {
    'processing_timestamp': str(datetime.utcnow()),
    'jobs_processed': original_count,
    'jobs_deduplicated': deduped_count,
    'duplicates_removed': duplicates_removed,
    'regions': regions_list,
    'seniority_levels': seniority_list
}

print("\nSummary:")
print(json.dumps(summary, indent=2))
