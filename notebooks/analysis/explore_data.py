# Databricks notebook source
# MAGIC %md
# MAGIC # Explore News Data
# MAGIC
# MAGIC Quick analysis of ingested RSS feeds

# COMMAND ----------

from pyspark.sql.functions import col, count, desc, to_date

# Read the data
df = spark.table("workspace.news_monitoring.raw_news_articles")

print(f"Total articles: {df.count()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Articles by Source

# COMMAND ----------

df.groupBy("source", "region") \
    .agg(count("*").alias("article_count")) \
    .orderBy("source") \
    .show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Recent Articles

# COMMAND ----------

df.select("source", "title", "published_date", "region", "url") \
    .orderBy(col("published_date").desc()) \
    .limit(20) \
    .show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Articles by Ingestion Date

# COMMAND ----------

df.groupBy("ingestion_date") \
    .agg(count("*").alias("articles")) \
    .orderBy("ingestion_date") \
    .show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sample Article Content

# COMMAND ----------

sample = df.select("source", "title", "description", "url") \
    .limit(5)

display(sample)
