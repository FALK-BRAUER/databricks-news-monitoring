# Task 003: Job Board Integration for CTO/VP Role Search

**Created:** November 29, 2025
**Status:** 🔄 In Progress
**Owner:** Falk Brauer

---

## 🎯 Objective

Build an automated job board aggregator that pulls CTO, VP Engineering, Solution Architect, and Presales roles from multiple sources (LinkedIn, Indeed, RemoteOK) via RSS feeds, stores them in Databricks, and displays them in the LinkedInOrganiser app.

---

## 📋 Task List

### ✅ Phase 1: Planning & Configuration
- [x] **1.1** Define job title search list (CTO, VP Eng, Solution Advisor, Presales, etc.)
  - Created: `config/job_titles.json`
  - 30 job titles across 3 categories (Executive, AI/ML, Solution/Presales)
  - Target regions: Germany, Switzerland, SEA, Remote

### 🔄 Phase 2: Data Ingestion
- [ ] **2.1** Create RSS job feed ingestion notebook for Databricks
  - File: `notebooks/ingestion/job_feeds.py`
  - Parse RSS/HTML feeds from multiple sources
  - Handle rate limiting and errors

- [ ] **2.2** Add LinkedIn Jobs RSS feeds
  - URL pattern: `https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search`
  - Query params: keywords, location, f_TPR (time posted)
  - Target ~30 title/location combinations

- [ ] **2.3** Add Indeed RSS feeds
  - URL pattern: `https://www.indeed.com/rss?q={title}&l={location}`
  - Simpler RSS structure
  - Good European coverage

- [ ] **2.4** Add RemoteOK RSS feeds
  - URL pattern: `https://remoteok.com/remote-{keyword}-jobs.rss`
  - Focus on remote roles
  - Often includes salary data

### ⏳ Phase 3: Data Processing
- [ ] **3.1** Create bronze table for raw job postings
  - Table: `workspace.news_monitoring.raw_job_postings`
  - Schema: job_id, title, company, location, description, url, source, posted_date
  - Partitioned by: source, ingestion_date

- [ ] **3.2** Create silver table with deduplication and enrichment
  - Table: `workspace.news_monitoring.silver_job_postings`
  - Deduplicate by URL/title across sources
  - Extract: salary, seniority level, company size, tech stack
  - Categorize: executive vs presales vs AI/ML

- [ ] **3.3** Create gold table for filtered CTO/VP jobs
  - Table: `workspace.news_monitoring.gold_job_opportunities`
  - Filter by: target regions, seniority level, job categories
  - Enrich with: company data from news articles, funding info

### ⏳ Phase 4: AI Matching
- [ ] **4.1** Add AI job matching/scoring logic
  - Score jobs 1-10 based on:
    - Title match (CTO > VP > Director)
    - Location preference (DE/CH/SEA = higher)
    - Company stage (Series B/C = higher)
    - Tech stack alignment
    - Salary competitiveness
  - Use Claude API for resume matching

### ⏳ Phase 5: UI Integration
- [ ] **5.1** Update LinkedInOrganiser news page to show jobs
  - Create new API route: `/api/jobs/search`
  - Display jobs with match scores
  - Filter by: region, job type, match score
  - Add "Save Job" and "Applied" tracking

- [ ] **5.2** Add job tracking features
  - Supabase table: saved_jobs, job_applications
  - Track status: Saved, Applied, Interview, Rejected, Offer
  - Add notes and follow-up reminders

### ⏳ Phase 6: Testing & Deployment
- [ ] **6.1** Test end-to-end job pipeline
  - Test RSS parsing for all sources
  - Verify deduplication logic
  - Check AI scoring accuracy
  - Test UI with real job data

- [ ] **6.2** Deploy to production
  - Upload notebooks to Databricks workspace
  - Create workflow job (daily at 6 AM Berlin time)
  - Configure email alerts for high-match jobs

---

## 📊 Target Job Sources

### LinkedIn Jobs
- **Format:** HTML/JSON API (public)
- **Coverage:** Global, best overall coverage
- **Pros:** Most comprehensive, good metadata
- **Cons:** Rate limiting, pagination needed
- **Example Queries:**
  - CTO in Germany
  - VP Engineering in Singapore
  - Solution Architect in Switzerland

### Indeed
- **Format:** RSS Feed
- **Coverage:** Strong in Europe and SEA
- **Pros:** Clean RSS, good descriptions
- **Cons:** Less startup coverage
- **Example Queries:**
  - CTO Germany
  - VP Engineering Switzerland
  - Presales Singapore

### RemoteOK
- **Format:** RSS Feed
- **Coverage:** Remote-first roles
- **Pros:** Salary data, tags, remote flexibility
- **Cons:** Smaller dataset
- **Example Queries:**
  - remote-cto-jobs
  - remote-vp-engineering-jobs

---

## 🎯 Success Criteria

1. **Coverage:** Collect 50+ relevant jobs per day across all sources
2. **Quality:** <10% duplicate jobs after deduplication
3. **Relevance:** 70%+ of jobs match target criteria (CTO/VP, target regions)
4. **Speed:** Full pipeline completes in <5 minutes
5. **AI Matching:** Match scores correlate with manual assessment (>80% agreement)
6. **User Experience:** Jobs display in app within 1 second

---

## 🔧 Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Job Board RSS Feeds                      │
│  LinkedIn Jobs │ Indeed │ RemoteOK │ (Future: More sources) │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              Bronze: Raw Job Postings                       │
│  - Ingest all feeds (job_feeds.py)                         │
│  - Store raw HTML/RSS data                                 │
│  - Dedupe by URL                                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              Silver: Enriched Job Postings                  │
│  - Extract structured fields                               │
│  - Categorize: Executive, AI/ML, Presales                 │
│  - Deduplicate across sources                             │
│  - Link to companies from news articles                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              Gold: Job Opportunities                        │
│  - Filter by target criteria                               │
│  - AI matching scores                                      │
│  - Rank by relevance                                       │
│  - Ready for UI display                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│            LinkedInOrganiser Web App                        │
│  - Browse jobs with filters                                │
│  - AI match explanations                                   │
│  - Save/track applications                                 │
│  - Get notifications for high matches                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
databricks-news-monitoring/
├── config/
│   └── job_titles.json              ✅ Created
├── notebooks/
│   └── ingestion/
│       └── job_feeds.py              ⏳ To create
│   └── transformation/
│       └── job_silver_layer.py       ⏳ To create
│       └── job_gold_layer.py         ⏳ To create
│       └── job_ai_matcher.py         ⏳ To create
└── sql/
    └── job_queries.sql               ⏳ To create

LinkedInOrganiser/linkedin-organizer-app/
├── app/api/jobs/
│   └── route.ts                      ⏳ To create
└── app/jobs/
    └── page.tsx                      ⏳ To create
```

---

## 🚀 Next Steps

1. **Immediate:** Build `job_feeds.py` notebook with RSS parsing
2. **Today:** Test LinkedIn + Indeed + RemoteOK feeds
3. **This Week:** Complete bronze → silver → gold pipeline
4. **Next Week:** Add AI matching and UI integration

---

## 📝 Notes

- Start with 6 core job titles × 4 locations = 24 RSS feeds
- Can expand to more titles/locations later
- Consider adding Wellfound API if RSS coverage insufficient
- Monitor rate limits: LinkedIn may throttle, use delays
- Legal: All sources are public RSS/APIs, safe to use

---

**Last Updated:** November 29, 2025
