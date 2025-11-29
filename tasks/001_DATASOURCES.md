# Task 001: Data Sources Configuration

**Date**: 2025-11-29
**Status**: In Progress
**Target Regions**: SEA, Australia, Hong Kong, Germany, Switzerland

---

## 📊 Summary

Analysis of available news sources for monitoring startups, scaleups, VC/PE activity, and job market in target regions.

---

## ✅ Working RSS Feeds (No Account Required)

### Verified & Production Ready

| Source | URL | Coverage | Status |
|--------|-----|----------|--------|
| **TechCrunch** | `https://techcrunch.com/feed/` | Global (includes SEA, AU when significant) | ✅ Working |
| **Tech.eu** | `https://tech.eu/feed/` | Europe (strong DE, CH coverage) | ✅ Working |
| **Crunchbase News** | `https://news.crunchbase.com/feed/` | Global VC/PE deals, funding | ✅ Working |

**Coverage Assessment**:
- 🟢 **Germany**: Good (Tech.eu)
- 🟢 **Switzerland**: Good (Tech.eu)
- 🟡 **SEA**: Limited (TechCrunch only)
- 🟡 **Australia**: Limited (TechCrunch only)
- 🟡 **Hong Kong**: Limited (TechCrunch only)

---

## ⚠️ RSS Feeds with Issues

| Source | URL | Issue | Alternative |
|--------|-----|-------|-------------|
| **Tech in Asia** | `https://www.techinasia.com/feed` | Cloudflare blocked | NewsAPI or scraping |
| **e27** | `https://e27.co/feed/` | Cloudflare blocked | NewsAPI or scraping |
| **DealStreetAsia** | `https://www.dealstreetasia.com/feed/` | Bot protection | NewsAPI or wait |

---

## 🔑 API-Based Sources

### NewsAPI (Recommended)

**URL**: https://newsapi.org/
**Cost**: FREE (100 requests/day)
**Signup Time**: 2 minutes

**Coverage by Region**:
- ✅ Singapore (`country=sg`)
- ✅ Australia (`country=au`)
- ✅ Hong Kong (`country=hk`)
- ✅ Germany (`country=de`)
- ✅ Switzerland (`country=ch`)

**Keyword Filtering**:
- "startup"
- "venture capital"
- "funding round"
- "scaleup"
- "private equity"

**Rate Limits**:
- Free: 100 requests/day
- Developer: 500 requests/day ($449/month)
- Business: 1000 requests/day ($999/month)

**Pros**:
- Clean, structured JSON
- Good regional coverage
- Real-time news
- Free tier sufficient for daily monitoring

**Cons**:
- Historical data limited to 1 month on free tier
- Rate limits

---

## 📍 Regional Coverage Analysis

### Southeast Asia (SEA)
**Working Sources**:
- TechCrunch (limited)
- NewsAPI with `country=sg` keyword filters

**Blocked/Issues**:
- Tech in Asia ❌
- e27 ❌
- DealStreetAsia ⚠️

**Recommendation**: NewsAPI required for good SEA coverage

### Australia
**Working Sources**:
- TechCrunch (limited)
- NewsAPI with `country=au`

**Recommendation**: NewsAPI + RSS for comprehensive coverage

### Hong Kong
**Working Sources**:
- TechCrunch (very limited)
- NewsAPI with `country=hk`

**Recommendation**: NewsAPI essential for HK coverage

### Germany
**Working Sources**:
- Tech.eu ✅
- TechCrunch (limited)
- NewsAPI with `country=de`

**Recommendation**: Tech.eu RSS + NewsAPI for comprehensive coverage

### Switzerland
**Working Sources**:
- Tech.eu ✅
- NewsAPI with `country=ch`

**Recommendation**: Tech.eu RSS provides good coverage

---

## 🎯 Recommended Implementation Strategy

### Phase 1: Immediate Start (No Accounts)

**Sources**:
1. TechCrunch RSS
2. Tech.eu RSS
3. Crunchbase News RSS

**Implementation Time**: 10-15 minutes
**Coverage**:
- 🟢 Good: Germany, Switzerland, Global VC deals
- 🟡 Limited: SEA, Australia, Hong Kong

---

### Phase 2: Enhanced Coverage (NewsAPI Required)

**Sources**:
1. All Phase 1 RSS feeds
2. NewsAPI with country filters

**Implementation Time**: 20-30 minutes (including signup)
**Coverage**:
- 🟢 Good: All target regions

**Requirements**:
- [ ] Sign up at https://newsapi.org/
- [ ] Get API key
- [ ] Add to AWS Secrets Manager
- [ ] Update config.yaml

---

## 💡 Implementation Decision

### Option A: Start with RSS Only
**Pros**: No account, start immediately, good Europe coverage
**Cons**: Limited SEA/AU/HK coverage

### Option B: RSS + NewsAPI (Recommended)
**Pros**: Comprehensive coverage, free tier, clean data
**Cons**: Requires signup, rate limits

---

## ✅ Decision Required

**Which option do you prefer?**
- [ ] **Option A**: Start with RSS only (TechCrunch, Tech.eu, Crunchbase)
- [ ] **Option B**: Sign up for NewsAPI + use RSS feeds
- [ ] **Option C**: Show me sample data first

---

**Created**: 2025-11-29
**Last Updated**: 2025-11-29
