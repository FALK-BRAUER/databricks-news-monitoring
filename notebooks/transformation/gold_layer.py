# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer - Analytics-Ready Datasets
# MAGIC
# MAGIC Creates aggregated, business-ready views for dashboards and analysis

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime

print("✓ Libraries imported")

# COMMAND ----------

# Configuration
SOURCE_TABLE = "workspace.news_monitoring.silver_articles"
CATALOG = "workspace"
SCHEMA = "news_monitoring"

print(f"Source: {SOURCE_TABLE}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Silver Data

# COMMAND ----------

silver_df = spark.table(SOURCE_TABLE)

print(f"Silver records: {silver_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Table 1: Daily Activity Summary

# COMMAND ----------

daily_activity = silver_df \
    .groupBy("ingestion_date", "region", "source") \
    .agg(
        count("*").alias("total_articles"),
        sum(when(col("has_funding"), 1).otherwise(0)).alias("funding_articles"),
        sum(when(col("has_acquisition"), 1).otherwise(0)).alias("acquisition_articles"),
        sum(when(col("is_layoff"), 1).otherwise(0)).alias("layoff_articles"),
        sum(when(col("is_hiring"), 1).otherwise(0)).alias("hiring_articles"),
        sum(col("funding_amount_usd")).alias("total_funding_usd"),
        collect_set(col("funding_round")).alias("funding_rounds_seen"),
        current_timestamp().alias("processed_at")
    ) \
    .orderBy("ingestion_date", "region")

daily_activity.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SCHEMA}.gold_daily_activity")

print(f"✓ Created: {CATALOG}.{SCHEMA}.gold_daily_activity")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Table 2: Funding Tracker

# COMMAND ----------

funding_tracker = silver_df \
    .filter(col("has_funding")) \
    .select(
        col("article_id"),
        col("title"),
        col("source"),
        col("region"),
        col("funding_round"),
        col("funding_amount_usd"),
        col("mentioned_companies"),
        col("published_date"),
        col("url"),
        col("ingestion_date")
    ) \
    .withColumn("funding_amount_millions", round(col("funding_amount_usd") / 1_000_000, 2)) \
    .orderBy(desc("published_date"))

funding_tracker.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SCHEMA}.gold_funding_tracker")

print(f"✓ Created: {CATALOG}.{SCHEMA}.gold_funding_tracker")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Table 3: Regional Trends

# COMMAND ----------

regional_trends = silver_df \
    .groupBy("region") \
    .agg(
        count("*").alias("total_articles"),
        count(when(col("has_funding"), 1)).alias("funding_count"),
        sum(col("funding_amount_usd")).alias("total_funding_usd"),
        count(when(col("has_acquisition"), 1)).alias("acquisition_count"),
        count(when(col("is_layoff"), 1)).alias("layoff_count"),
        count(when(col("is_hiring"), 1)).alias("hiring_count"),
        countDistinct("source").alias("source_count"),
        max("ingestion_date").alias("latest_data_date")
    ) \
    .withColumn("total_funding_billions", round(col("total_funding_usd") / 1_000_000_000, 2)) \
    .withColumn("avg_funding_per_deal_millions",
                round(col("total_funding_usd") / col("funding_count") / 1_000_000, 2)) \
    .orderBy(desc("total_articles"))

regional_trends.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SCHEMA}.gold_regional_trends")

print(f"✓ Created: {CATALOG}.{SCHEMA}.gold_regional_trends")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Table 4: Company Mentions

# COMMAND ----------

# Explode companies and count mentions
company_mentions = silver_df \
    .select(
        explode("mentioned_companies").alias("company"),
        "source",
        "region",
        "article_categories",
        "has_funding",
        "has_acquisition",
        "ingestion_date"
    ) \
    .groupBy("company", "region") \
    .agg(
        count("*").alias("mention_count"),
        sum(when(col("has_funding"), 1).otherwise(0)).alias("funding_mentions"),
        sum(when(col("has_acquisition"), 1).otherwise(0)).alias("acquisition_mentions"),
        collect_set("source").alias("sources"),
        max("ingestion_date").alias("last_mentioned")
    ) \
    .filter(col("mention_count") >= 2) \
    .orderBy(desc("mention_count"))

company_mentions.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SCHEMA}.gold_company_mentions")

print(f"✓ Created: {CATALOG}.{SCHEMA}.gold_company_mentions")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Table 5: Category Analysis

# COMMAND ----------

category_analysis = silver_df \
    .select(
        explode("article_categories").alias("category"),
        "source",
        "region",
        "ingestion_date",
        "published_date"
    ) \
    .groupBy("category", "region") \
    .agg(
        count("*").alias("article_count"),
        countDistinct("source").alias("source_count"),
        max("ingestion_date").alias("latest_date")
    ) \
    .orderBy("region", desc("article_count"))

category_analysis.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOG}.{SCHEMA}.gold_category_analysis")

print(f"✓ Created: {CATALOG}.{SCHEMA}.gold_category_analysis")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Statistics

# COMMAND ----------

print("\n" + "="*80)
print("GOLD LAYER CREATED")
print("="*80)

print("\nTables created:")
print(f"  1. {CATALOG}.{SCHEMA}.gold_daily_activity")
print(f"  2. {CATALOG}.{SCHEMA}.gold_funding_tracker")
print(f"  3. {CATALOG}.{SCHEMA}.gold_regional_trends")
print(f"  4. {CATALOG}.{SCHEMA}.gold_company_mentions")
print(f"  5. {CATALOG}.{SCHEMA}.gold_category_analysis")

print("\nSample insights:")

# Regional overview
print("\n--- Regional Overview ---")
spark.table(f"{CATALOG}.{SCHEMA}.gold_regional_trends") \
    .select("region", "total_articles", "funding_count", "total_funding_billions") \
    .show()

# Top companies
print("\n--- Top Mentioned Companies ---")
spark.table(f"{CATALOG}.{SCHEMA}.gold_company_mentions") \
    .select("company", "region", "mention_count", "funding_mentions") \
    .limit(10) \
    .show(truncate=False)

# Recent funding
print("\n--- Recent Funding Rounds ---")
spark.table(f"{CATALOG}.{SCHEMA}.gold_funding_tracker") \
    .select("title", "funding_round", "funding_amount_millions", "region") \
    .limit(10) \
    .show(truncate=False)

print("\n" + "="*80)
print(f"Processing complete: {datetime.utcnow().isoformat()}")
print("="*80)
