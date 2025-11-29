# Databricks notebook source
# MAGIC %md
# MAGIC # CTO/VP Opportunity Detector
# MAGIC
# MAGIC Identifies companies in transition that likely need senior tech leadership

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime, timedelta

print("✓ Libraries imported")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Silver Data

# COMMAND ----------

silver_df = spark.table("workspace.news_monitoring.silver_articles")

print(f"Total articles: {silver_df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Opportunity Signals

# COMMAND ----------

def detect_opportunity_signals(title, description, content):
    """
    Detect signals that indicate CTO/VP hiring opportunity
    Returns: list of signals detected
    """
    text = f"{title or ''} {description or ''} {content or ''}".lower()

    signals = []

    # 1. FRESH FUNDING (Strong signal)
    if any(word in text for word in ['series b', 'series c', 'raised', 'funding round', 'closes']):
        signals.append('fresh_funding')

    # 2. REGIONAL EXPANSION (Very strong for regional VP roles)
    expansion_keywords = [
        'expands to', 'expansion', 'opens office', 'new office',
        'enters market', 'launches in', 'regional', 'apac',
        'emea', 'opens', 'establishes presence'
    ]
    if any(word in text for word in expansion_keywords):
        signals.append('regional_expansion')

    # 3. LEADERSHIP CHANGES (Direct signal)
    leadership_keywords = [
        'cto', 'chief technology', 'vp engineering', 'vp product',
        'head of engineering', 'head of technology', 'chief technical',
        'appoints', 'joins as', 'new cto', 'leadership team',
        'executive team', 'c-suite'
    ]
    if any(word in text for word in leadership_keywords):
        signals.append('leadership_change')

    # 4. AGGRESSIVE HIRING
    hiring_keywords = [
        'hiring', 'recruitment', 'doubles team', 'expands team',
        'aggressive hiring', 'hiring spree', 'looking for',
        'jobs', 'careers', 'join our team'
    ]
    if any(word in text for word in hiring_keywords):
        signals.append('aggressive_hiring')

    # 5. PRODUCT/TECH TRANSFORMATION
    tech_keywords = [
        'platform', 'rebuilds', 'migrates to', 'ai transformation',
        'digital transformation', 'cloud migration', 'modernization',
        'new platform', 'tech stack', 'architecture'
    ]
    if any(word in text for word in tech_keywords):
        signals.append('tech_transformation')

    # 6. ACQUISITION ACTIVITY
    if any(word in text for word in ['acquired', 'acquisition', 'merger', 'acquires']):
        signals.append('acquisition_activity')

    # 7. RAPID GROWTH
    growth_keywords = [
        'rapid growth', 'fastest growing', 'scales', 'doubles revenue',
        'unicorn', 'valuation', 'growth', 'scaling'
    ]
    if any(word in text for word in growth_keywords):
        signals.append('rapid_growth')

    return signals

# Register UDF
detect_signals_udf = udf(detect_opportunity_signals, ArrayType(StringType()))

print("✓ Signal detection UDF defined")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Detect Opportunities

# COMMAND ----------

# Apply signal detection
opportunities_df = silver_df \
    .withColumn("opportunity_signals", detect_signals_udf(col("title"), col("description"), col("content"))) \
    .withColumn("signal_count", size(col("opportunity_signals"))) \
    .withColumn("has_fresh_funding", array_contains(col("opportunity_signals"), "fresh_funding")) \
    .withColumn("has_expansion", array_contains(col("opportunity_signals"), "regional_expansion")) \
    .withColumn("has_leadership_change", array_contains(col("opportunity_signals"), "leadership_change")) \
    .withColumn("has_aggressive_hiring", array_contains(col("opportunity_signals"), "aggressive_hiring")) \
    .withColumn("has_tech_transformation", array_contains(col("opportunity_signals"), "tech_transformation"))

# Calculate opportunity score
opportunities_df = opportunities_df \
    .withColumn("opportunity_score",
        (when(col("has_fresh_funding"), 3).otherwise(0) +
         when(col("has_expansion"), 4).otherwise(0) +  # Highest score for regional roles
         when(col("has_leadership_change"), 5).otherwise(0) +  # Direct signal
         when(col("has_aggressive_hiring"), 2).otherwise(0) +
         when(col("has_tech_transformation"), 2).otherwise(0) +
         when(array_contains(col("opportunity_signals"), "acquisition_activity"), 2).otherwise(0) +
         when(array_contains(col("opportunity_signals"), "rapid_growth"), 1).otherwise(0))
    )

print("✓ Opportunity signals detected")

# COMMAND ----------

# MAGIC %md
# MAGIC ## High-Priority Opportunities

# COMMAND ----------

# Filter for high-signal opportunities
high_priority = opportunities_df \
    .filter(col("signal_count") >= 2) \
    .filter(col("opportunity_score") >= 5) \
    .select(
        "article_id",
        "title",
        "source",
        "region",
        "opportunity_signals",
        "opportunity_score",
        "funding_round",
        "funding_amount_usd",
        "mentioned_companies",
        "published_date",
        "url",
        "has_fresh_funding",
        "has_expansion",
        "has_leadership_change",
        "ingestion_date"
    ) \
    .orderBy(desc("opportunity_score"), desc("published_date"))

print(f"\nHigh-priority opportunities found: {high_priority.count()}")

# Show top opportunities
print("\n🎯 TOP CTO/VP OPPORTUNITIES:")
high_priority.select(
    "title",
    "opportunity_score",
    "opportunity_signals",
    "region",
    "funding_round"
).show(20, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save Opportunity Leads

# COMMAND ----------

# Create gold table for opportunities
high_priority.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("workspace.news_monitoring.gold_cto_opportunities")

print(f"✓ Saved to: workspace.news_monitoring.gold_cto_opportunities")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Company Opportunity Profile

# COMMAND ----------

# Aggregate by company to build profiles
company_opportunities = opportunities_df \
    .select(
        explode("mentioned_companies").alias("company"),
        "opportunity_signals",
        "funding_round",
        "funding_amount_usd",
        "region",
        "has_fresh_funding",
        "has_expansion",
        "has_leadership_change",
        "published_date"
    ) \
    .groupBy("company", "region") \
    .agg(
        count("*").alias("mention_count"),
        sum(when(col("has_fresh_funding"), 1).otherwise(0)).alias("funding_signals"),
        sum(when(col("has_expansion"), 1).otherwise(0)).alias("expansion_signals"),
        sum(when(col("has_leadership_change"), 1).otherwise(0)).alias("leadership_signals"),
        max("funding_round").alias("latest_funding_round"),
        max("funding_amount_usd").alias("latest_funding_amount"),
        max("published_date").alias("last_mentioned"),
        flatten(collect_list("opportunity_signals")).alias("all_signals")
    ) \
    .withColumn("total_signals",
        col("funding_signals") + col("expansion_signals") + col("leadership_signals")) \
    .filter(col("total_signals") >= 1) \
    .orderBy(desc("total_signals"), desc("last_mentioned"))

company_opportunities.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("workspace.news_monitoring.gold_company_leads")

print(f"✓ Saved to: workspace.news_monitoring.gold_company_leads")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary Report

# COMMAND ----------

print("\n" + "="*80)
print("CTO/VP OPPORTUNITY DETECTION SUMMARY")
print("="*80)

print(f"\nTotal articles analyzed: {opportunities_df.count()}")
print(f"High-priority opportunities: {high_priority.count()}")
print(f"Companies with signals: {company_opportunities.count()}")

print("\n--- Signal Breakdown ---")
opportunities_df.select(explode("opportunity_signals").alias("signal")) \
    .groupBy("signal") \
    .count() \
    .orderBy(desc("count")) \
    .show()

print("\n--- Top Company Leads ---")
company_opportunities \
    .select("company", "region", "total_signals", "funding_signals",
            "expansion_signals", "leadership_signals") \
    .limit(15) \
    .show(truncate=False)

print("\n--- Recent High-Score Opportunities ---")
high_priority \
    .select("title", "opportunity_score", "region", "url") \
    .limit(10) \
    .show(truncate=False)

print("\n" + "="*80)
print(f"Processing complete: {datetime.utcnow().isoformat()}")
print("="*80)
