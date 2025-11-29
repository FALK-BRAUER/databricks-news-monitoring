# Databricks notebook source
# MAGIC %md
# MAGIC # Minimal Test Notebook
# MAGIC
# MAGIC This notebook tests basic serverless functionality.

# COMMAND ----------

print("=" * 80)
print("MINIMAL SERVERLESS TEST")
print("=" * 80)

# Test basic Python functionality
print("\n✓ Python is working")

# Test Spark
print("\n✓ Spark session:")
print(f"  App Name: {spark.sparkContext.appName}")
print(f"  Spark Version: {spark.version}")

# Test creating a simple DataFrame
data = [
    {"id": 1, "name": "Test Article 1", "source": "test"},
    {"id": 2, "name": "Test Article 2", "source": "test"}
]

df = spark.createDataFrame(data)
print("\n✓ Created test DataFrame:")
df.show()

print("\n=" * 80)
print("TEST COMPLETED SUCCESSFULLY")
print("=" * 80)
