-- ============================================================================
-- CTO/VP JOB OPPORTUNITY QUERIES
-- Find companies in transition that need senior tech leadership
-- ============================================================================

-- Query 1: TOP CTO/VP OPPORTUNITIES
-- Highest scoring opportunities with multiple signals
SELECT
    title,
    opportunity_score,
    opportunity_signals,
    region,
    funding_round,
    ROUND(funding_amount_usd / 1000000, 2) as funding_millions,
    mentioned_companies,
    url,
    DATE(published_date) as date
FROM workspace.news_monitoring.gold_cto_opportunities
WHERE opportunity_score >= 7  -- High confidence
ORDER BY opportunity_score DESC, published_date DESC
LIMIT 25;

-- ============================================================================
-- Query 2: REGIONAL EXPANSION OPPORTUNITIES
-- Companies expanding to new regions (great for regional VP roles)
SELECT
    title,
    region,
    mentioned_companies,
    opportunity_signals,
    url,
    DATE(published_date) as date
FROM workspace.news_monitoring.gold_cto_opportunities
WHERE has_expansion = true
ORDER BY published_date DESC;

-- ============================================================================
-- Query 3: LEADERSHIP CHANGES (Direct Signal)
-- Companies with C-suite/leadership announcements
SELECT
    title,
    region,
    mentioned_companies,
    funding_round,
    url,
    DATE(published_date) as date
FROM workspace.news_monitoring.gold_cto_opportunities
WHERE has_leadership_change = true
ORDER BY opportunity_score DESC, published_date DESC;

-- ============================================================================
-- Query 4: FRESH FUNDING + HIRING
-- Best combo: just raised money and actively hiring
SELECT
    title,
    funding_round,
    ROUND(funding_amount_usd / 1000000, 2) as funding_millions,
    region,
    mentioned_companies,
    url,
    DATE(published_date) as date
FROM workspace.news_monitoring.gold_cto_opportunities
WHERE has_fresh_funding = true
  AND has_aggressive_hiring = true
ORDER BY funding_amount_usd DESC NULLS LAST, published_date DESC;

-- ============================================================================
-- Query 5: COMPANY LEADS - Ranked by Signals
-- Companies to research based on multiple signals over time
SELECT
    company,
    region,
    total_signals,
    funding_signals,
    expansion_signals,
    leadership_signals,
    latest_funding_round,
    ROUND(latest_funding_amount / 1000000, 2) as latest_funding_millions,
    last_mentioned,
    all_signals
FROM workspace.news_monitoring.gold_company_leads
WHERE total_signals >= 2
ORDER BY total_signals DESC, last_mentioned DESC;

-- ============================================================================
-- Query 6: SERIES B/C COMPANIES (Scaling Stage)
-- Companies at the perfect stage for senior hires
SELECT
    c.company,
    c.region,
    c.total_signals,
    c.latest_funding_round,
    ROUND(c.latest_funding_amount / 1000000, 2) as funding_millions,
    c.expansion_signals,
    c.leadership_signals,
    c.last_mentioned
FROM workspace.news_monitoring.gold_company_leads c
WHERE c.latest_funding_round IN ('SERIES B', 'SERIES C', 'B', 'C')
ORDER BY c.latest_funding_amount DESC NULLS LAST;

-- ============================================================================
-- Query 7: GERMANY/SWITZERLAND OPPORTUNITIES
-- Target regions for your search
SELECT
    title,
    opportunity_score,
    opportunity_signals,
    funding_round,
    mentioned_companies,
    url,
    DATE(published_date) as date
FROM workspace.news_monitoring.gold_cto_opportunities
WHERE region = 'europe'
  AND opportunity_score >= 5
ORDER BY opportunity_score DESC, published_date DESC;

-- ============================================================================
-- Query 8: SOUTHEAST ASIA OPPORTUNITIES
-- SEA market opportunities
SELECT
    title,
    opportunity_score,
    opportunity_signals,
    funding_round,
    mentioned_companies,
    url,
    DATE(published_date) as date
FROM workspace.news_monitoring.gold_cto_opportunities
WHERE region = 'sea'
  AND opportunity_score >= 5
ORDER BY opportunity_score DESC, published_date DESC;

-- ============================================================================
-- Query 9: RECENT OPPORTUNITIES (Last 7 Days)
-- What's hot right now
SELECT
    title,
    opportunity_score,
    opportunity_signals,
    region,
    mentioned_companies,
    url,
    DATE(published_date) as date,
    DATEDIFF(CURRENT_DATE, DATE(published_date)) as days_ago
FROM workspace.news_monitoring.gold_cto_opportunities
WHERE DATE(published_date) >= CURRENT_DATE - INTERVAL 7 DAYS
ORDER BY opportunity_score DESC, published_date DESC;

-- ============================================================================
-- Query 10: TECH TRANSFORMATION PROJECTS
-- Companies undergoing platform/tech changes (need technical leadership)
SELECT
    title,
    opportunity_signals,
    region,
    mentioned_companies,
    url,
    DATE(published_date) as date
FROM workspace.news_monitoring.gold_cto_opportunities
WHERE has_tech_transformation = true
ORDER BY opportunity_score DESC, published_date DESC;

-- ============================================================================
-- Query 11: MULTI-SIGNAL COMPANIES (High Confidence)
-- Companies mentioned in multiple contexts (funding + expansion + hiring)
SELECT
    company,
    region,
    total_signals,
    funding_signals,
    expansion_signals,
    leadership_signals,
    latest_funding_round,
    CASE
        WHEN funding_signals > 0 AND expansion_signals > 0 THEN 'Funding + Expansion'
        WHEN funding_signals > 0 AND leadership_signals > 0 THEN 'Funding + Leadership Change'
        WHEN expansion_signals > 0 AND leadership_signals > 0 THEN 'Expansion + Leadership Change'
        ELSE 'Multiple Signals'
    END as opportunity_type,
    last_mentioned
FROM workspace.news_monitoring.gold_company_leads
WHERE total_signals >= 3
ORDER BY total_signals DESC, last_mentioned DESC
LIMIT 30;

-- ============================================================================
-- Query 12: WEEKLY DIGEST - Top 10 Opportunities
-- Use this for weekly email summary
WITH ranked_opportunities AS (
    SELECT
        title,
        opportunity_score,
        opportunity_signals,
        region,
        funding_round,
        mentioned_companies,
        url,
        DATE(published_date) as date,
        ROW_NUMBER() OVER (PARTITION BY region ORDER BY opportunity_score DESC) as rank_in_region
    FROM workspace.news_monitoring.gold_cto_opportunities
    WHERE DATE(published_date) >= CURRENT_DATE - INTERVAL 7 DAYS
)
SELECT
    region,
    title,
    opportunity_score,
    opportunity_signals,
    funding_round,
    mentioned_companies,
    url,
    date
FROM ranked_opportunities
WHERE rank_in_region <= 3
ORDER BY region, opportunity_score DESC;

-- ============================================================================
-- Query 13: COMPANIES TO RESEARCH
-- Create a personal watchlist
SELECT DISTINCT
    c.company,
    c.region,
    c.total_signals,
    c.latest_funding_round,
    ROUND(c.latest_funding_amount / 1000000, 2) as funding_millions,
    c.last_mentioned,
    CONCAT('https://www.google.com/search?q=', REPLACE(c.company, ' ', '+'), '+careers') as google_careers_search
FROM workspace.news_monitoring.gold_company_leads c
WHERE c.total_signals >= 2
  AND c.last_mentioned >= CURRENT_DATE - INTERVAL 30 DAYS
ORDER BY c.total_signals DESC, c.latest_funding_amount DESC NULLS LAST
LIMIT 50;
