# Data Sources for News Monitoring

Target Regions: **SEA, Australia, Hong Kong, Germany, Switzerland**

## 📰 Free RSS Feeds (No Account Needed)

### Global Tech/Startup News
- ✅ **TechCrunch** - `https://techcrunch.com/feed/`
  - Coverage: Global (including SEA, AU when significant)
  - Focus: Startups, VC funding, tech news

- ✅ **Crunchbase News** - `https://news.crunchbase.com/feed/`
  - Coverage: Global funding rounds, exits, M&A
  - Focus: VC/PE deals, startup funding

### Southeast Asia (SEA)
- ⚠️ **Tech in Asia** - RSS blocked by Cloudflare
  - Alternative: May need web scraping or API

- ⚠️ **e27** - RSS blocked by Cloudflare
  - Alternative: May need web scraping or API

- **DealStreetAsia** - `https://www.dealstreetasia.com/feed/`
  - Coverage: SEA startup funding, VC/PE news
  - Focus: Deals, exits, investors

- **KrAsia** - `https://kr-asia.com/feed`
  - Coverage: SEA tech and startups
  - Owned by 36Kr (China tech media)

### Australia
- **StartupDaily** - `https://www.startupdaily.net/feed/`
  - Coverage: Australian startups

- **SmartCompany** - `https://www.smartcompany.com.au/startupsmart/feed/`
  - Coverage: Australian startups and small business

- **AustralianFinTech** - `https://australianfintech.com.au/feed/`
  - Coverage: Australian fintech sector

### Hong Kong
- **TechNode** - May have RSS (need to verify)
  - Coverage: Hong Kong & Greater China tech

- **Forkast News** - Blockchain/Web3 focus (Hong Kong based)
  - May require scraping

### Europe (Germany & Switzerland)
- ✅ **Tech.eu** - `https://tech.eu/feed/`
  - Coverage: European tech, strong DE/CH coverage
  - Focus: Startups, funding, exits

- **Deutsche Startups** - `https://www.deutsche-startups.de/feed/`
  - Coverage: German startup ecosystem
  - Language: German

- **SwissTech.news** - May have RSS
  - Coverage: Swiss startups

- **StartupTicker** (Switzerland) - `https://www.startupticker.ch/en/rss-feed`
  - Coverage: Swiss startup news

---

## 🔑 API-Based Sources (Account Required)

### NewsAPI (Free Tier: 100 requests/day)
**Sign up**: https://newsapi.org/

**Coverage**: Can filter by:
- Country codes: `sg` (Singapore), `au` (Australia), `hk` (Hong Kong), `de` (Germany), `ch` (Switzerland)
- Keywords: "startup", "venture capital", "funding", "scaleup"
- Categories: business, technology

**Pros**:
- Clean, structured data
- 100 requests/day free
- Real-time news

**Cons**:
- Limited historical data (1 month on free tier)
- Rate limits

### GNews API (Free Tier: 100 requests/day)
**Sign up**: https://gnews.io/

**Coverage**: Similar to NewsAPI
- Country filtering
- Keyword search
- Language filtering

**Pros**:
- Good international coverage
- Free tier available

### NewsData.io (Free Tier: 200 requests/day)
**Sign up**: https://newsdata.io/

**Coverage**:
- Better Asian coverage than NewsAPI
- Supports SEA countries well

### Crunchbase API (Paid)
**Sign up**: https://www.crunchbase.com/products/crunchbase-api

**Coverage**:
- Company data, funding rounds
- Investor information
- M&A activity

**Pricing**: Starts at $49/month

**Alternative**: Use Crunchbase News RSS (free) instead of API

---

## 🎯 Recommended Approach

### Phase 1: Start with Free RSS (Immediate)
1. **TechCrunch** - Global coverage
2. **Tech.eu** - Europe (DE, CH)
3. **DealStreetAsia** - SEA
4. **StartupDaily** - Australia
5. **Crunchbase News** - VC/PE deals

### Phase 2: Add News APIs (Need signup)
1. **NewsAPI** (free tier)
   - Set up country filters for: SG, AU, HK, DE, CH
   - Keywords: startup, funding, venture capital, scaleup

2. **GNews API** (free tier as backup)

### Phase 3: Premium Sources (Optional)
- Crunchbase API for detailed company/investor data
- Web scraping for blocked RSS feeds (Tech in Asia, e27)

---

## 📊 Data Coverage by Region

| Region | Free RSS | News API | Coverage Level |
|--------|----------|----------|----------------|
| SEA | ⚠️ Limited | ✅ Good | Medium |
| Australia | ✅ Good | ✅ Good | Good |
| Hong Kong | ⚠️ Limited | ✅ Good | Medium |
| Germany | ✅ Good | ✅ Good | Good |
| Switzerland | ✅ Good | ✅ Good | Good |

---

## 🚀 Next Steps

**Option A: Quick Start (No accounts needed)**
- Implement RSS feeds listed in Phase 1
- Start collecting data immediately
- Limited coverage for SEA/HK

**Option B: Comprehensive (Requires 1 account)**
- Sign up for NewsAPI (5 minutes)
- Implement RSS + NewsAPI
- Better regional coverage

**Recommendation**: Start with Option A (RSS only), then add NewsAPI once RSS is working.
