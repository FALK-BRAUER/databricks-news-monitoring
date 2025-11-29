# 🎯 Your CTO/VP Job Search Intelligence Platform

**Built:** November 29, 2025
**Status:** ✅ Production Ready
**Purpose:** Find companies in transition that need senior tech leadership

---

## 🚀 What You Have Now

### **1. Expanded Data Collection**
✅ **14 RSS feeds** (was 4) collecting ~300+ articles/day

**New Sources Added:**
- 🇪🇺 **Sifted** - European startups (DE, CH, UK, FR)
- 🇪🇺 **EU-Startups** - Pan-European news
- 🇩🇪 **Deutsche Startups** - Germany/Switzerland/Austria
- 🌏 **KrASIA** - SEA + Hong Kong
- 🇸🇬 **Vulcan Post** - Singapore/Malaysia
- 💼 **Protocol** - Tech leadership news
- 📊 **BuiltIn SF** - Job market signals
- 💰 **VC Journal** - Investment news
- 💰 **PitchBook** - Deals & funding
- 📰 **Techmeme** - Tech headlines

---

### **2. Opportunity Detection System**

**Automatically detects 7 hiring signals:**

| Signal | Score | What It Means |
|--------|-------|---------------|
| 👔 Leadership Change | 5 | CTO/VP position open or just filled |
| 🌍 Regional Expansion | 4 | Opening new office = regional VP needed |
| 💰 Fresh Funding | 3 | Series B/C = scaling team |
| 💼 Aggressive Hiring | 2 | "Hiring spree" mentioned |
| 🔧 Tech Transformation | 2 | Platform rebuild = need tech lead |
| 🤝 Acquisition | 2 | Integration = new roles |
| 📈 Rapid Growth | 1 | Scaling pains |

**Opportunity Score:** Sum of signals (7+ = high priority)

---

### **3. New Data Tables**

**`gold_cto_opportunities`**
- Articles with multiple hiring signals
- Ranked by opportunity score
- Direct links to articles

**`gold_company_leads`**
- Companies aggregated by signals over time
- Funding history
- Regional presence
- Best companies to research

---

### **4. Daily Email Digest** (Optional)

**Sends you every morning at 8 AM Berlin time:**
- Top 10 opportunities from last 24 hours
- Company leads with multiple signals
- Direct links to articles and company career pages

**To enable:** Add SendGrid API key to secrets

---

## 🔍 How to Use It

### **Quick Start - Find Opportunities Now:**

```sql
-- Open Databricks SQL and run:

-- 1. TOP OPPORTUNITIES
SELECT title, opportunity_score, opportunity_signals,
       region, mentioned_companies, url
FROM workspace.news_monitoring.gold_cto_opportunities
WHERE opportunity_score >= 7
ORDER BY opportunity_score DESC
LIMIT 20;

-- 2. COMPANIES TO RESEARCH
SELECT company, region, total_signals,
       funding_signals, expansion_signals, leadership_signals,
       latest_funding_round
FROM workspace.news_monitoring.gold_company_leads
WHERE total_signals >= 2
ORDER BY total_signals DESC
LIMIT 30;

-- 3. GERMANY/SWITZERLAND FOCUS
SELECT title, opportunity_score, mentioned_companies, url
FROM workspace.news_monitoring.gold_cto_opportunities
WHERE region = 'europe'
  AND opportunity_score >= 5
ORDER BY opportunity_score DESC;
```

---

### **Pre-Built Queries**

See `sql/cto_job_opportunities.sql` for 13 ready-to-use queries:

1. Top opportunities (high score)
2. Regional expansion (great for VP roles)
3. Leadership changes (direct signal)
4. Fresh funding + hiring (best combo)
5. Company leads ranked
6. Series B/C companies (scaling stage)
7. Germany/Switzerland focus
8. Southeast Asia focus
9. Recent opportunities (last 7 days)
10. Tech transformation projects
11. Multi-signal companies
12. Weekly digest
13. Companies to research with Google search links

---

## 📊 Your Workflow

### **Every Morning:**

1. **Check Email Digest** (if enabled)
   - Top opportunities sent to falk.brauer@me.com
   - Companies to watch

2. **Or Query Databricks SQL**
   - Run query #9 (recent opportunities)
   - Get last 7 days of leads

3. **Research Top Companies**
   - Check LinkedIn company pages
   - Visit career pages
   - Google "[Company] CTO" or "[Company] VP Engineering"

4. **Act on Opportunities**
   - Apply if role is posted
   - Connect with recruiters on LinkedIn
   - Network with current employees
   - Set up Google Alerts for companies

---

## 🎯 What Gets Flagged

### **Perfect Scenarios for CTO/VP Roles:**

**Scenario 1: Regional Expansion**
```
"Stripe expands to Singapore, opens new APAC office"
→ Score: 4-5 (expansion signal)
→ Action: They need regional VP/CTO for APAC
```

**Scenario 2: Fresh Funding + Hiring**
```
"Company X raises $50M Series B, plans to triple team"
→ Score: 5-6 (funding + hiring)
→ Action: Scaling = need senior leadership
```

**Scenario 3: Leadership Announcement**
```
"Company Y appoints new CTO, joining from Google"
→ Score: 5 (leadership change)
→ Action: Follow the company, more roles likely coming
```

**Scenario 4: Tech Transformation**
```
"Company Z migrates to cloud, modernizes platform"
→ Score: 2-4 (transformation)
→ Action: Need technical leadership for migration
```

---

## 📈 Your Data Pipeline

### **Runs Daily at 8 AM Berlin Time:**

```
1. Bronze: Ingest 14 RSS feeds (~300 articles)
          ↓
2. Silver: Extract entities (companies, funding, categories)
          ↓
3. Gold: Create analytics tables
          ↓
4. Opportunities: Detect hiring signals
          ↓
5. Email: Send you daily digest (optional)
```

**Workflow URL:** https://dbc-5a365369-15d1.cloud.databricks.com/#job/82343254902219

---

## 🔧 Next Steps to Maximize This

### **Week 1: Manual Research**
- [ ] Query top 30 companies from `gold_company_leads`
- [ ] Check their LinkedIn pages
- [ ] Visit career pages manually
- [ ] Follow companies on LinkedIn
- [ ] Set up Google Alerts for top 10 companies

### **Week 2: Network Building**
- [ ] Connect with CTOs/VPs at target companies
- [ ] Join relevant LinkedIn groups
- [ ] Engage with company posts
- [ ] Message recruiters

### **Month 1: Add Premium Data**
- [ ] Get Crunchbase API ($29/mo) - **HIGHLY RECOMMENDED**
- [ ] Add LinkedIn scraping (Bright Data or Apify)
- [ ] Monitor career pages automatically
- [ ] Track The Org for leadership changes

---

## 💰 Recommended Investments

### **Free (Current Setup)**
✅ 14 RSS feeds
✅ Opportunity detection
✅ SQL queries
✅ Email digest (with SendGrid free tier)

### **Low Cost ($50-100/month)**
🎯 **Crunchbase API** ($29-99/mo)
   - Best ROI for your use case
   - Comprehensive funding data
   - Employee count changes
   - Leadership movements

🎯 **The Org** ($49/mo)
   - Track CTO/VP movements
   - Org chart changes
   - Direct hiring signals

### **Premium ($200-500/month)**
- Full data suite (Crunchbase + LinkedIn + Career pages)
- Worth it if actively job searching

---

## 📧 Email Digest Setup (Optional)

**To enable daily emails:**

1. Get SendGrid API key (free tier: 100 emails/day)
2. Add to AWS Secrets Manager:
```bash
aws secretsmanager update-secret \
  --secret-id AWS \
  --secret-string '{"SENDGRID_API_KEY":"your-key-here"}'
```

3. Upload daily_digest notebook
4. Workflow will send email every morning

---

## 🎯 Success Metrics

**Track your progress:**
- Companies researched per week
- Applications submitted
- Networking connections made
- Interviews scheduled

**Platform metrics:**
- Opportunities detected: Check daily
- High-score leads (7+): Priority targets
- Regional focus: DE/CH/SEA matches your targets

---

## 🚀 Quick Wins This Week

### **Action Items:**

**Today:**
1. ✅ Run SQL query #1 (top opportunities)
2. ✅ Research top 5 companies
3. ✅ Check their career pages

**This Week:**
1. Query opportunities daily
2. Research 20-30 companies total
3. Apply to 5-10 senior roles
4. Connect with 10 recruiters/CTOs on LinkedIn

**This Month:**
1. Get Crunchbase API
2. Build company watchlist
3. Set up Google Alerts
4. Track applications in spreadsheet

---

## 📖 Documentation

**Main Files:**
- `CTO_JOB_SEARCH_PLATFORM.md` (this file)
- `DATA_SOURCES_FOR_JOB_SEARCH.md` - expansion plan
- `sql/cto_job_opportunities.sql` - 13 queries
- `SUMMARY.md` - overall platform overview

---

## 💡 Pro Tips

**For Your Job Search:**

1. **Focus on Series B/C companies** - They're scaling and need leadership
2. **Regional expansion is gold** - VP/Regional CTO roles
3. **Fresh funding = hiring budget** - Apply within 3 months of funding
4. **Leadership changes = opportunities** - New CTO often builds team
5. **Tech transformations need leaders** - Platform rebuilds, migrations

**Red Flags to Avoid:**
- Companies with layoff signals
- Funding rounds <$10M (too early for senior roles)
- Companies without clear tech focus

---

## 🎉 What You've Built

You now have a **production-grade job search intelligence platform** that:

✅ Monitors 14 news sources automatically
✅ Detects 7 types of hiring signals
✅ Scores opportunities 1-10
✅ Tracks companies over time
✅ Can email you daily opportunities
✅ Provides 13 pre-built queries
✅ Focuses on YOUR target regions (DE, CH, SEA)
✅ Runs completely automated

**This is like having a personal job search assistant running 24/7.**

---

**Your next CTO/VP role might be in today's digest. Go check your opportunities! 🚀**

**Query to run right now:**
```sql
SELECT * FROM workspace.news_monitoring.gold_cto_opportunities
WHERE opportunity_score >= 7
ORDER BY opportunity_score DESC;
```

Good luck with your search! 🎯
