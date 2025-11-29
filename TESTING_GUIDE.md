# Testing Guide: RSS Feed Ingestion Notebook

## 📋 Quick Start - Manual Testing

Since automated cluster creation requires specific AWS permissions, here's how to test the notebook manually in the Databricks UI:

### Step 1: Open Databricks Workspace

1. Go to: https://dbc-5a365369-15d1.cloud.databricks.com
2. Sign in with your credentials

### Step 2: Navigate to the Notebook

1. Click on **Workspace** in the left sidebar
2. Navigate to: `/Users/flk.brauer@gmail.com/news-monitoring/`
3. Click on: `rss_feeds.py`

### Step 3: Attach to a Cluster

1. At the top of the notebook, you'll see "Detached"
2. Click the dropdown
3. Options:
   - **Create a new cluster** (recommended for first test)
     - Click "Create compute"
     - Select: **Single node**
     - Runtime: **13.3 LTS (Scala 2.12, Spark 3.4.1)** or later
     - Node type: **m5d.large** or any available small instance
     - Termination: **30 minutes** of inactivity
     - Click "Create"
   - Or use an existing running cluster if available

### Step 4: Run the Notebook

**Option A: Run All Cells**
1. Once cluster is attached and running (green dot)
2. Click: **Run All** button at the top
3. Wait 2-3 minutes for completion

**Option B: Run Cell by Cell** (Recommended for first time)
1. Click **Run** on each cell sequentially
2. Watch the output as it processes
3. Review results after each step

### Step 5: What to Expect

The notebook will:

1. ✅ **Setup** - Import libraries (5 seconds)
2. ✅ **Install Dependencies** - Install feedparser (10 seconds)
3. ✅ **Load Config** - Display configuration (instant)
4. ✅ **Define Functions** - RSS parser code (instant)
5. ✅ **Fetch Feeds** - Download articles (~10 seconds)
   - Expected: ~86 articles total
   - TechCrunch: ~20 articles
   - Tech.eu: ~20 articles
   - Tech in Asia: ~36 articles
   - Crunchbase News: ~10 articles
6. ✅ **Convert to DataFrame** - Create Spark DF (5 seconds)
7. ✅ **Create Table** - Set up Delta Lake (10 seconds)
8. ✅ **Write Data** - Save to Delta (10 seconds)
9. ✅ **Verify** - Query and display results (5 seconds)
10. ✅ **Summary** - Final report (instant)

**Total Time: ~2-3 minutes**

---

## 📊 Expected Output

### Fetch Summary
```
================================================================================
SUMMARY: Fetched 86 articles
================================================================================

Articles by Source:
  crunchbase_news     :  10 articles
  tech_eu             :  20 articles
  tech_in_asia        :  36 articles
  techcrunch          :  20 articles

Articles by Region:
  europe              :  20 articles
  global              :  30 articles
  sea                 :  36 articles
```

### Delta Lake Table Created
- **Table**: `main.news_monitoring.raw_news_articles`
- **Partitions**: By `source` and `ingestion_date`
- **Records**: 86 articles (first run)

### Sample Articles Displayed
You'll see a table with recent startup news from:
- Supabase $5B valuation
- India's e-commerce IPOs
- European tech funding rounds
- Southeast Asia startup news

---

## ✅ Success Indicators

After running, you should see:

1. **No Errors** - All cells completed successfully
2. **Article Count** - "Fetched 86 articles" (approximately)
3. **Table Created** - "Successfully wrote 86 articles to main.news_monitoring.raw_news_articles"
4. **Data Verification** - Tables showing data by source and region
5. **JSON Summary** - Final summary with breakdown

---

## 🔍 Verify Data in Delta Lake

After the notebook runs, you can query the data:

```python
# Run this in a new cell or new notebook
df = spark.table("main.news_monitoring.raw_news_articles")

# Show total records
print(f"Total articles: {df.count()}")

# Show breakdown
df.groupBy("source", "region").count().show()

# Show latest articles
df.orderBy("ingestion_timestamp", ascending=False).select(
    "source", "title", "published_date", "region"
).show(10, truncate=50)
```

---

## 🐛 Troubleshooting

### Issue: Cluster won't start
**Solution**:
- Try a different instance type (m5d.large, m5.xlarge, etc.)
- Check your Databricks workspace has compute permissions
- Contact your Databricks admin for instance availability

### Issue: "Module not found: feedparser"
**Solution**:
- Make sure the `%pip install feedparser python-dateutil --quiet` cell ran successfully
- Restart the Python interpreter if needed

### Issue: "Table already exists" error
**Solution**:
- This is normal on subsequent runs
- The notebook appends new data to existing table
- To start fresh: `DROP TABLE main.news_monitoring.raw_news_articles`

### Issue: Fewer than 86 articles
**Possible Causes**:
- RSS feeds may have fewer items at different times
- Network issues fetching feeds
- Check the logs for specific feed failures

---

## 🚀 Next Steps After Successful Test

Once the notebook runs successfully:

1. **Review the Data**
   - Browse articles in the Delta table
   - Check data quality
   - Verify regional coverage

2. **Schedule Automated Runs**
   - Create a Databricks Job/Workflow
   - Schedule: Daily at 2:00 AM UTC
   - Email notifications on failure

3. **Build Transformations**
   - Clean and enrich data
   - Extract entities (companies, investors)
   - Add sentiment analysis

4. **Create Dashboards**
   - Databricks SQL queries
   - Visualizations by region
   - Funding trends over time

---

## 📞 Need Help?

If you encounter issues:

1. **Check Cell Output** - Look for error messages in red
2. **Check Cluster Logs** - Click on cluster name → "Logs"
3. **Simplify** - Run cells one at a time to isolate the issue
4. **Screenshot** - Capture the error for troubleshooting

---

## ✨ Automated Testing (Future)

Once your AWS/Databricks configuration allows cluster creation, we can automate this with:
- CI/CD pipeline
- Scheduled testing
- Automated data quality checks
- Slack/email notifications

For now, manual testing in the UI is the most reliable approach!

---

**Happy Testing!** 🎉

The notebook is ready and waiting at:
**https://dbc-5a365369-15d1.cloud.databricks.com/#workspace/Users/flk.brauer@gmail.com/news-monitoring/rss_feeds.py**
