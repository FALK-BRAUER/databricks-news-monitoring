# Workflow Management Guide

## 📋 Overview

The **News Monitoring - Daily RSS Ingestion** workflow automatically fetches news articles from RSS feeds and stores them in Delta Lake.

**Job ID**: `615194712900735`
**Job URL**: https://dbc-5a365369-15d1.cloud.databricks.com/#job/615194712900735

---

## ⏰ Schedule

- **Frequency**: Daily
- **Time**: 2:00 AM UTC
- **Timezone**: UTC
- **Status**: Active (UNPAUSED)
- **Cron Expression**: `0 0 2 * * ?`

---

## 📊 What the Workflow Does

### Task: `ingest_rss_feeds`

1. **Fetches RSS Feeds** (~10 seconds)
   - TechCrunch (Global startup news)
   - Tech.eu (Europe: DE, CH)
   - Tech in Asia (Southeast Asia)
   - Crunchbase News (VC/PE deals)

2. **Parses Articles** (~5 seconds)
   - Extracts title, description, URL, date, author
   - Tags with region and categories
   - Generates unique article IDs

3. **Writes to Delta Lake** (~10 seconds)
   - Table: `main.news_monitoring.raw_news_articles`
   - Partitions: By `source` and `ingestion_date`
   - Mode: Append (preserves history)

4. **Verifies Data** (~5 seconds)
   - Counts articles by source/region
   - Displays sample data
   - Generates summary report

**Total Runtime**: ~2-3 minutes
**Expected Articles**: 80-120 per run

---

## 📧 Notifications

### Email Alerts

- **Recipient**: falk.brauer@me.com
- **On Failure**: Yes ✅
- **On Success**: No
- **On Start**: No

---

## 💻 Compute Configuration

- **Type**: Serverless
- **Auto-scaling**: Managed by Databricks
- **Cost**: Pay-per-use serverless compute

---

## 🎛️ Managing the Workflow

### View Job Status

```bash
# Via Web UI
https://dbc-5a365369-15d1.cloud.databricks.com/#job/615194712900735

# Via CLI
databricks jobs get --job-id 615194712900735
```

### Run Manually (Test)

**Option 1: Via Web UI**
1. Go to job URL above
2. Click "Run Now" button
3. Monitor execution in real-time

**Option 2: Via CLI**
```bash
databricks jobs run-now --job-id 615194712900735
```

**Option 3: Via API**
```bash
curl -X POST \
  https://dbc-5a365369-15d1.cloud.databricks.com/api/2.1/jobs/run-now \
  -H "Authorization: Bearer $DATABRICKS_API_KEY" \
  -d '{"job_id": 615194712900735}'
```

### Pause/Resume Schedule

**Pause Workflow:**
```bash
# Via API
curl -X POST \
  https://dbc-5a365369-15d1.cloud.databricks.com/api/2.1/jobs/update \
  -H "Authorization: Bearer $DATABRICKS_API_KEY" \
  -d '{
    "job_id": 615194712900735,
    "new_settings": {
      "schedule": {
        "quartz_cron_expression": "0 0 2 * * ?",
        "timezone_id": "UTC",
        "pause_status": "PAUSED"
      }
    }
  }'
```

**Resume Workflow:**
- Change `"pause_status": "PAUSED"` to `"pause_status": "UNPAUSED"`

### View Run History

**Via Web UI:**
1. Go to job URL
2. Click "Runs" tab
3. See all historical runs with status

**Via CLI:**
```bash
databricks jobs runs list --job-id 615194712900735 --limit 10
```

### View Latest Run

```bash
databricks jobs runs list --job-id 615194712900735 --limit 1
```

---

## 📈 Monitoring

### Key Metrics to Monitor

1. **Run Status** - Should complete successfully
2. **Article Count** - Should be 80-120 articles per run
3. **Runtime** - Should complete in 2-3 minutes
4. **Failures** - Email alert sent automatically

### Query Recent Data

```sql
-- Check latest ingestion
SELECT
  source,
  COUNT(*) as article_count,
  MAX(ingestion_timestamp) as latest_ingestion
FROM main.news_monitoring.raw_news_articles
WHERE ingestion_date = CURRENT_DATE()
GROUP BY source
ORDER BY source;

-- View recent articles
SELECT
  source,
  title,
  published_date,
  region,
  url
FROM main.news_monitoring.raw_news_articles
WHERE ingestion_date = CURRENT_DATE()
ORDER BY ingestion_timestamp DESC
LIMIT 10;
```

---

## 🔧 Troubleshooting

### Job Failed

**Check:**
1. View run logs in Databricks UI
2. Check email notification for error details
3. Verify RSS feeds are accessible
4. Check notebook hasn't been modified

**Common Issues:**
- **Network timeout**: RSS feed temporarily down
- **Schema mismatch**: Delta table schema changed
- **Quota exceeded**: Serverless compute limits

**Resolution:**
- Re-run the job manually
- Check RSS feed URLs
- Review error stack trace in logs

### No Articles Fetched

**Possible Causes:**
- RSS feeds returned no new items
- Network issues
- Feed format changed

**Resolution:**
- Check feed URLs manually in browser
- Review notebook logs
- Verify `feedparser` library working

### Duplicate Articles

**Check:**
- Articles should have unique `article_id` (MD5 hash of URL)
- Deduplication happens automatically by URL

**Resolution:**
- If duplicates exist, add deduplication logic in transformation layer

---

## 🔄 Updating the Workflow

### Update Schedule

1. Edit `workflows/rss_ingestion_serverless.json`
2. Modify `quartz_cron_expression`
3. Deploy update via API:

```bash
python3 << 'EOF'
import requests
import json

host = "https://dbc-5a365369-15d1.cloud.databricks.com"
token = "YOUR_TOKEN_HERE"
job_id = "615194712900735"

with open('workflows/rss_ingestion_serverless.json', 'r') as f:
    new_settings = json.load(f)

url = f"{host}/api/2.1/jobs/update"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
payload = {"job_id": job_id, "new_settings": new_settings}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
EOF
```

### Update Notebook

1. Edit `notebooks/ingestion/rss_feeds.py`
2. Upload to workspace:
```bash
databricks workspace import \
  notebooks/ingestion/rss_feeds.py \
  /Users/flk.brauer@gmail.com/news-monitoring/rss_feeds.py \
  --language PYTHON \
  --format SOURCE \
  --overwrite
```

### Add New RSS Feed

1. Edit `notebooks/ingestion/rss_feeds.py`
2. Add feed to `CONFIG['data_sources']['news_apis'][0]['feeds']`
3. Upload updated notebook
4. Test manually before next scheduled run

---

## 📊 Performance Optimization

### Current Configuration
- **Compute**: Serverless (optimal for this workload)
- **Partitioning**: By source and date
- **Write Mode**: Append

### Future Optimizations
- **Z-Ordering**: On frequently queried columns
- **Vacuum**: Remove old data files
- **Optimize**: Compact small files
- **Incremental**: Only fetch new articles

---

## 🗑️ Deleting the Workflow

**⚠️ Warning**: This will permanently delete the scheduled job.

```bash
# Via API
curl -X POST \
  https://dbc-5a365369-15d1.cloud.databricks.com/api/2.1/jobs/delete \
  -H "Authorization: Bearer $DATABRICKS_API_KEY" \
  -d '{"job_id": 615194712900735}'
```

---

## 📞 Support

**Issues?**
- Check job logs in Databricks UI
- Review email notifications
- Query Delta table for data validation

**Configuration Files:**
- Job Config: `workflows/rss_ingestion_serverless.json`
- Job ID: `workflows/job_id.txt`
- Notebook: `notebooks/ingestion/rss_feeds.py`

---

**Workflow Status**: ✅ Active and Scheduled
**Next Run**: Daily at 2:00 AM UTC
**Monitoring**: Email notifications enabled
