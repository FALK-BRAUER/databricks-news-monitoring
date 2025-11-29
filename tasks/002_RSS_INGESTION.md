# Task 002: RSS Feed Ingestion Implementation

**Date**: 2025-11-29
**Status**: In Progress
**Priority**: High
**Depends On**: 001_DATASOURCES

---

## 🎯 Objective

Build and deploy RSS feed ingestion to collect startup, VC/PE, and software news from 4 verified sources covering SEA, Australia, Hong Kong, Germany, and Switzerland.

---

## 📋 Scope

### Data Sources (Phase 1)

| Source | URL | Region | Articles/Day |
|--------|-----|--------|--------------|
| TechCrunch | `https://techcrunch.com/feed/` | Global | ~50-100 |
| Tech.eu | `https://tech.eu/feed/` | Europe (DE, CH) | ~20-30 |
| Tech in Asia | `https://www.techinasia.com/feed` | SEA | ~30-50 |
| Crunchbase News | `https://news.crunchbase.com/feed/` | Global | ~10-20 |

**Total Expected Volume**: 110-200 articles/day

---

## 🏗️ Implementation Plan

### Step 1: Local Python Script
- [x] Create RSS parser using `feedparser`
- [x] Handle User-Agent requirements (Tech in Asia)
- [x] Parse standard fields: title, description, url, date, author
- [x] Extract regional metadata
- [x] Test with all 4 feeds
- [x] Save output as JSON for review

### Step 2: Data Structure
```python
{
    "article_id": "uuid",
    "source": "techcrunch",
    "title": "Article title",
    "description": "Article description",
    "content": "Full content if available",
    "url": "https://...",
    "author": "Author name",
    "published_date": "2025-11-29T12:00:00Z",
    "categories": ["startup", "funding"],
    "region": "sea",
    "country_codes": ["sg"],
    "ingestion_timestamp": "2025-11-29T12:05:00Z",
    "raw_data": {...}  # Original RSS item
}
```

### Step 3: Databricks Notebook
- [ ] Convert script to Databricks notebook
- [ ] Add Delta Lake write logic
- [ ] Implement error handling
- [ ] Add logging and monitoring
- [ ] Test on Databricks cluster

### Step 4: Deployment
- [ ] Upload notebook to workspace
- [ ] Create Databricks workflow
- [ ] Schedule daily runs (2:00 AM UTC)
- [ ] Set up email alerts

---

## 🔧 Technical Details

### Libraries Required
```python
feedparser==6.0.10
requests>=2.31.0
python-dateutil>=2.8.2
```

### User-Agent Handling
```python
# Tech in Asia requires browser User-Agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
```

### Error Handling
- Network timeouts (30 seconds)
- Invalid RSS/XML parsing
- Missing required fields
- Duplicate detection

---

## ✅ Success Criteria

1. **Functionality**
   - [ ] Successfully fetch all 4 RSS feeds
   - [ ] Parse 100% of articles without errors
   - [ ] Extract all required fields
   - [ ] Handle User-Agent requirements

2. **Data Quality**
   - [ ] No duplicate articles in single run
   - [ ] All dates in ISO format
   - [ ] Valid URLs for all articles
   - [ ] Proper regional tagging

3. **Performance**
   - [ ] Complete ingestion in < 2 minutes
   - [ ] Handle 200+ articles per run
   - [ ] Minimal memory footprint

4. **Monitoring**
   - [ ] Log article counts per source
   - [ ] Alert on failed feeds
   - [ ] Track ingestion duration

---

## 📊 Expected Output

### Sample Data Volume
- **Daily**: 110-200 articles
- **Weekly**: 770-1400 articles
- **Monthly**: ~3,300-6,000 articles

### Regional Breakdown (Estimated)
- Global/Multiple: 60-120 articles/day
- Europe (DE, CH): 20-30 articles/day
- SEA: 30-50 articles/day

---

## 🚀 Execution Steps

### Phase 1: Local Development (Today)
1. Create `src/data_sources/rss_parser.py`
2. Test with all 4 feeds
3. Generate sample output
4. Review data quality

### Phase 2: Databricks Integration (Next)
1. Create `notebooks/ingestion/rss_feeds.py`
2. Test on Databricks workspace
3. Write to Delta Lake bronze layer
4. Verify data in tables

### Phase 3: Automation (Final)
1. Create Databricks workflow
2. Schedule daily runs
3. Set up monitoring
4. Document runbook

---

## 🐛 Known Issues & Mitigations

| Issue | Impact | Mitigation |
|-------|--------|------------|
| Tech in Asia requires User-Agent | Fails without header | Add User-Agent to request |
| RSS feeds may change format | Parsing errors | Flexible schema, error handling |
| Network timeouts | Missing data | Retry logic, alerting |
| Duplicate articles | Data quality | Hash-based deduplication |

---

## 📈 Future Enhancements

- [ ] Add keyword filtering for software focus
- [ ] Extract funding amounts from content
- [ ] NLP entity extraction (companies, investors)
- [ ] Sentiment analysis
- [ ] Incremental processing (only new articles)

---

## 📝 Deliverables

1. ✅ `src/data_sources/rss_parser.py` - RSS parsing utilities
2. ⏳ `notebooks/ingestion/rss_feeds.py` - Databricks ingestion notebook
3. ⏳ Sample output JSON file
4. ⏳ Test results and data quality report

---

**Created**: 2025-11-29
**Assigned To**: Claude
**Estimated Time**: 2-3 hours
**Actual Time**: TBD
