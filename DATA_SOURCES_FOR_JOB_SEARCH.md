# 🎯 Data Sources for CTO/VP Job Search

## Current Status
✅ **4 RSS Feeds** collecting ~100 articles/day
✅ **Opportunity detector** finding hiring signals
✅ **Company leads** ranked by transition signals

---

## 🚀 HIGH-PRIORITY ADDITIONS (Do First)

### 1. **LinkedIn Company Pages** (CRITICAL)
**Why:** Direct hiring signals, job postings, leadership announcements

**What to scrape:**
- Job posting counts by company (spike = hiring spree)
- Leadership changes ("X joined as CTO")
- Company announcements
- Employee count growth

**Implementation:**
- Use Apify LinkedIn scraper OR
- Bright Data LinkedIn dataset OR
- Build custom scraper (needs LinkedIn account)

**Signals:**
- "We're hiring!" posts
- Multiple VP/CTO job postings
- New office announcements
- "Join our growing team"

**Value:** ⭐⭐⭐⭐⭐ (DIRECT job postings)

---

### 2. **Company Career Pages** (HIGH PRIORITY)
**Why:** See ACTUAL open positions

**Target companies from your leads:**
- Check `/careers` or `/jobs` pages
- Track new "VP Engineering", "CTO", "Head of Engineering" postings
- Monitor posting frequency (rapid hiring = growth)

**Implementation:**
- Scrape career pages of companies in gold_company_leads
- Track new postings daily
- Alert on senior tech roles

**Value:** ⭐⭐⭐⭐⭐ (DIRECT opportunities)

---

### 3. **Wellfound (AngelList Talent)** (HIGH PRIORITY)
**Why:** Startup-specific job board with detailed company info

**Data available:**
- Open roles at startups
- Company funding stage
- Team size
- Tech stack
- Salary ranges

**API:** Yes (requires account)

**Value:** ⭐⭐⭐⭐⭐ (Startup-focused, great for CTO roles)

---

### 4. **Crunchbase API** (HIGH PRIORITY)
**Why:** Most comprehensive startup funding database

**Data available:**
- Funding rounds with exact amounts
- Investor details
- Employee count changes
- Acquisitions
- Leadership changes
- Office locations

**API:** Yes (paid, but worth it)
**Cost:** ~$29-99/month

**Signals:**
- Recent funding (especially Series B/C)
- Rapid headcount growth
- New regional offices
- Executive departures

**Value:** ⭐⭐⭐⭐⭐ (Gold standard for startup data)

---

### 5. **Glassdoor Reviews** (MEDIUM PRIORITY)
**Why:** Culture insights, growth indicators

**Data available:**
- Employee reviews
- Interview experiences
- "Pros: Fast growing" = scaling signal
- Engineering team size mentions
- CTO/leadership reviews

**Value:** ⭐⭐⭐⭐ (Quality/culture screening)

---

## 📰 ADDITIONAL NEWS SOURCES

### 6. **Tech News Sites (Region-Specific)**

**Europe:**
- **Sifted** (European startups) - RSS available
- **EU-Startups** - RSS available
- **The Org** (org chart changes) - leadership tracking

**Southeast Asia:**
- **KrASIA** - Tech/startup news
- **Vulcan Post** (Malaysia/Singapore)
- **TechNode** (China/SEA overlap)

**Germany/Switzerland Specific:**
- **Deutsche Startups** (German)
- **Swiss Startup News**
- **Berlin Valley**

**Value:** ⭐⭐⭐⭐ (Regional insights)

---

### 7. **Press Release Aggregators**
- **PR Newswire** - Company announcements
- **Business Wire** - Funding/leadership news
- **Company press pages** - Direct from source

**Value:** ⭐⭐⭐ (Official announcements)

---

## 🔍 SPECIALIZED SOURCES

### 8. **The Org** (org-chart-as-a-service)
**Why:** Track executive movements

- Who's joining/leaving as CTO/VP
- Company org structure
- Direct hiring signals

**Value:** ⭐⭐⭐⭐⭐ (Leadership changes)

---

### 9. **BuiltIn** (Regional Tech Hubs)
- BuiltIn Austin, NYC, Berlin, etc.
- Company profiles
- Job listings
- Funding news

**Value:** ⭐⭐⭐⭐ (Regional focus)

---

### 10. **Product Hunt**
**Why:** New product launches = scaling signal

- Companies launching products
- Often hiring after product launch
- Shows tech stack/focus

**Value:** ⭐⭐⭐ (Innovation signal)

---

## 💼 EXECUTIVE JOB BOARDS

### 11. **Executive-Specific Boards**
- **Exec** (YC network)
- **CTO Jobs** (cto-jobs.com)
- **TechMeAbroad** (international tech jobs)
- **TopTal** (senior freelance → full-time)

**Value:** ⭐⭐⭐⭐ (Targeted to your level)

---

## 🤖 AI-ENHANCED DATA

### 12. **Company Website Scraping**
**What to track:**
- "About Us" page (team size mentioned)
- Leadership page (changes)
- News/blog section
- Investor pages

**Value:** ⭐⭐⭐ (Direct from source)

---

## 📊 IMPLEMENTATION PRIORITY

### **Phase 1: Quick Wins (This Week)**
1. ✅ Opportunity detector (DONE)
2. ⏳ Add 5-10 regional RSS feeds
3. ⏳ Set up Wellfound scraper
4. ⏳ Manual check of top 20 company career pages

### **Phase 2: High Value (Next 2 Weeks)**
1. Crunchbase API integration
2. LinkedIn company scraper
3. The Org integration
4. Career page monitoring

### **Phase 3: Comprehensive (Month 1)**
1. Glassdoor integration
2. Press release feeds
3. Executive job boards
4. AI-powered company research

---

## 🎯 RECOMMENDED NEXT STEPS FOR YOU

### **Immediate Actions:**

**1. Query Your Opportunities (Now):**
```sql
-- Run this in Databricks SQL
SELECT * FROM workspace.news_monitoring.gold_cto_opportunities
WHERE opportunity_score >= 7
ORDER BY opportunity_score DESC;
```

**2. Add These RSS Feeds (30 min):**
- Sifted (Europe): https://sifted.eu/feed
- EU-Startups: https://www.eu-startups.com/feed/
- Deutsche Startups: https://www.deutsche-startups.de/feed/

**3. Manual Research (This Week):**
- Take top 20 companies from `gold_company_leads`
- Check their career pages manually
- Follow on LinkedIn
- Set Google Alerts

**4. Set Up Alerts (1 hour):**
I can build you a daily email with:
- Top 5 opportunities from yesterday
- Companies with multiple signals
- Regional expansion announcements

---

## 💰 BUDGET RECOMMENDATIONS

**Free Tier:**
- RSS feeds (free)
- Manual career page checks (free)
- LinkedIn manual (free)

**Low Cost ($50-100/month):**
- Crunchbase API ($29-99/mo) - **HIGHLY RECOMMENDED**
- Bright Data (web scraping) ($50/mo)

**Premium ($200-500/month):**
- Full Crunchbase Pro
- The Org subscription
- Apify LinkedIn scrapers
- Multiple data sources

---

## 🚀 What Should We Build Next?

**Option A: Add 10 RSS Feeds + Career Page Monitor (2 hours)**
- Quick wins, immediate value
- Double your data coverage

**Option B: Crunchbase Integration (4 hours)**
- Best signal quality
- Comprehensive company data
- Worth the API cost

**Option C: Daily Email Digest (2 hours)**
- Email you top opportunities every morning
- Saves you from manual checking
- Actionable leads

**What would help you most right now?**

I recommend: **Option A + Option C** (add feeds + daily email)
Then add Crunchbase when budget allows.
