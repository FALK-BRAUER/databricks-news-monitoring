# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer - Cleaned and Enriched News
# MAGIC
# MAGIC Transforms raw RSS data into cleaned, categorized articles with extracted entities

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install Dependencies

# COMMAND ----------

%pip install spacy textblob

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
import re
from datetime import datetime

print("✓ Libraries imported")

# COMMAND ----------

# Configuration
SOURCE_TABLE = "workspace.news_monitoring.raw_news_articles"
TARGET_TABLE = "workspace.news_monitoring.silver_articles"

print(f"Source: {SOURCE_TABLE}")
print(f"Target: {TARGET_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Extraction Functions

# COMMAND ----------

# Define UDFs for entity extraction

def extract_funding_info(text):
    """Extract funding amounts and rounds from text"""
    if not text:
        return None, None

    text = str(text).lower()

    # Funding rounds
    round_patterns = [
        r'series ([a-f])',
        r'(seed) round',
        r'(pre-seed)',
        r'series ([a-f])\+',
        r'(ipo)',
        r'(acquisition|acquired)',
    ]

    funding_round = None
    for pattern in round_patterns:
        match = re.search(pattern, text)
        if match:
            funding_round = match.group(1).upper() if match.group(1) else match.group(0).upper()
            break

    # Funding amounts
    amount_patterns = [
        r'\$(\d+(?:\.\d+)?)\s*(billion|bn)',
        r'\$(\d+(?:\.\d+)?)\s*(million|mn|m)\b',
        r'(\d+(?:\.\d+)?)\s*(billion|bn)',
        r'(\d+(?:\.\d+)?)\s*(million|mn|m)\b',
    ]

    funding_amount_usd = None
    for pattern in amount_patterns:
        match = re.search(pattern, text)
        if match:
            amount = float(match.group(1))
            unit = match.group(2).lower()

            if 'b' in unit:
                funding_amount_usd = amount * 1_000_000_000
            else:
                funding_amount_usd = amount * 1_000_000
            break

    return funding_round, funding_amount_usd

def categorize_article(title, description):
    """Categorize article based on content"""
    text = f"{title or ''} {description or ''}".lower()

    categories = []

    # Funding
    if any(word in text for word in ['funding', 'raises', 'raised', 'series', 'investment', 'round', 'closes']):
        categories.append('funding')

    # Acquisition
    if any(word in text for word in ['acquisition', 'acquired', 'acquires', 'merger', 'bought', 'buys']):
        categories.append('acquisition')

    # Product
    if any(word in text for word in ['launches', 'launched', 'unveils', 'released', 'announces', 'introduces', 'new product']):
        categories.append('product_launch')

    # Layoffs / Hiring
    if any(word in text for word in ['layoffs', 'laid off', 'job cuts', 'downsizing', 'redundancies']):
        categories.append('layoffs')
    elif any(word in text for word in ['hiring', 'jobs', 'recruitment', 'careers']):
        categories.append('hiring')

    # IPO
    if any(word in text for word in ['ipo', 'going public', 'public offering', 'lists on']):
        categories.append('ipo')

    # Partnership
    if any(word in text for word in ['partnership', 'partners with', 'collaboration', 'teams up']):
        categories.append('partnership')

    # Expansion
    if any(word in text for word in ['expansion', 'expands', 'enters market', 'opens office']):
        categories.append('expansion')

    return categories if categories else ['general']

def extract_companies(text):
    """Extract potential company names"""
    if not text:
        return []

    # Simple extraction - look for capitalized words
    # In production, use NER (Named Entity Recognition) with spaCy
    words = str(text).split()
    companies = []

    for i, word in enumerate(words):
        # If word starts with capital and is 2+ chars
        if word and len(word) > 1 and word[0].isupper():
            # Check if next word is also capitalized (multi-word company name)
            if i < len(words) - 1 and len(words[i+1]) > 1 and words[i+1][0].isupper():
                companies.append(f"{word} {words[i+1]}")
            else:
                companies.append(word)

    # Remove duplicates and common words
    stop_words = {'The', 'A', 'An', 'In', 'On', 'At', 'To', 'For', 'Of', 'And', 'Or', 'But'}
    companies = list(set([c for c in companies if c not in stop_words]))

    return companies[:5]  # Return top 5

# Register UDFs
extract_funding_udf = udf(extract_funding_info, StructType([
    StructField("funding_round", StringType()),
    StructField("funding_amount_usd", DoubleType())
]))

categorize_udf = udf(categorize_article, ArrayType(StringType()))
extract_companies_udf = udf(extract_companies, ArrayType(StringType()))

print("✓ UDFs defined")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load and Transform Data

# COMMAND ----------

# Read bronze data
bronze_df = spark.table(SOURCE_TABLE)

print(f"Bronze records: {bronze_df.count()}")

# COMMAND ----------

# Apply transformations
silver_df = bronze_df \
    .withColumn("full_text", concat_ws(" ", col("title"), col("description"), col("content"))) \
    .withColumn("funding_info", extract_funding_udf(col("full_text"))) \
    .withColumn("funding_round", col("funding_info.funding_round")) \
    .withColumn("funding_amount_usd", col("funding_info.funding_amount_usd")) \
    .withColumn("article_categories", categorize_udf(col("title"), col("description"))) \
    .withColumn("mentioned_companies", extract_companies_udf(col("title"))) \
    .withColumn("has_funding", col("funding_round").isNotNull()) \
    .withColumn("has_acquisition", array_contains(col("article_categories"), "acquisition")) \
    .withColumn("is_layoff", array_contains(col("article_categories"), "layoffs")) \
    .withColumn("is_hiring", array_contains(col("article_categories"), "hiring")) \
    .withColumn("published_timestamp", to_timestamp(col("published_date"))) \
    .withColumn("days_since_published", datediff(current_date(), to_date(col("published_date")))) \
    .withColumn("processing_timestamp", current_timestamp()) \
    .drop("funding_info", "full_text")

print("✓ Transformations applied")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Checks

# COMMAND ----------

print("Data Quality Summary:")
print(f"  Total articles: {silver_df.count()}")
print(f"  With funding info: {silver_df.filter(col('has_funding')).count()}")
print(f"  Acquisitions: {silver_df.filter(col('has_acquisition')).count()}")
print(f"  Layoffs: {silver_df.filter(col('is_layoff')).count()}")
print(f"  Hiring: {silver_df.filter(col('is_hiring')).count()}")

print("\nArticles by category:")
silver_df.select(explode("article_categories").alias("category")) \
    .groupBy("category") \
    .count() \
    .orderBy(desc("count")) \
    .show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Silver Table

# COMMAND ----------

# Create schema if needed
spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.news_monitoring")

# Write to silver table
silver_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .partitionBy("source", "ingestion_date") \
    .saveAsTable(TARGET_TABLE)

print(f"✓ Silver table created: {TARGET_TABLE}")
print(f"  Records written: {silver_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Output

# COMMAND ----------

print("Sample enriched articles:")
display(
    silver_df
    .filter(col("has_funding") | col("has_acquisition"))
    .select(
        "source",
        "title",
        "funding_round",
        "funding_amount_usd",
        "article_categories",
        "mentioned_companies",
        "region",
        "published_date"
    )
    .limit(10)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

summary = {
    "processing_timestamp": datetime.utcnow().isoformat(),
    "bronze_records": bronze_df.count(),
    "silver_records": silver_df.count(),
    "funding_articles": silver_df.filter(col("has_funding")).count(),
    "acquisition_articles": silver_df.filter(col("has_acquisition")).count()
}

print("\n" + "="*80)
print("SILVER LAYER PROCESSING COMPLETE")
print("="*80)
print(f"""
Bronze → Silver Transformation Summary:
  Input records:       {summary['bronze_records']}
  Output records:      {summary['silver_records']}
  Funding detected:    {summary['funding_articles']}
  Acquisitions:        {summary['acquisition_articles']}

Target table: {TARGET_TABLE}
""")
print("="*80)
