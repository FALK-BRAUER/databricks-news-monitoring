-- ============================================================================
-- Databricks SQL Dashboard Queries
-- News Monitoring - Startup & VC Intelligence
-- ============================================================================

-- Query 1: Regional Activity Overview
-- Shows total articles, funding activity, and trends by region
SELECT
    region,
    total_articles,
    funding_count,
    total_funding_billions,
    acquisition_count,
    layoff_count,
    hiring_count,
    ROUND(100.0 * funding_count / total_articles, 1) as funding_percentage
FROM workspace.news_monitoring.gold_regional_trends
ORDER BY total_articles DESC;

-- ============================================================================
-- Query 2: Recent Funding Rounds
-- Latest funding announcements with deal sizes
SELECT
    title,
    funding_round,
    funding_amount_millions as amount_usd_millions,
    region,
    mentioned_companies,
    DATE(published_date) as date,
    source
FROM workspace.news_monitoring.gold_funding_tracker
WHERE published_date >= CURRENT_DATE - INTERVAL 30 DAYS
ORDER BY published_date DESC
LIMIT 20;

-- ============================================================================
-- Query 3: Daily Activity Trend
-- Shows article volume over time by region
SELECT
    ingestion_date,
    region,
    SUM(total_articles) as articles,
    SUM(funding_articles) as funding_news,
    SUM(acquisition_articles) as acquisitions,
    SUM(total_funding_usd) / 1000000 as total_funding_millions
FROM workspace.news_monitoring.gold_daily_activity
GROUP BY ingestion_date, region
ORDER BY ingestion_date DESC, region;

-- ============================================================================
-- Query 4: Top Companies by Mentions
-- Most frequently mentioned companies across all sources
SELECT
    company,
    region,
    mention_count,
    funding_mentions,
    acquisition_mentions,
    last_mentioned,
    CASE
        WHEN funding_mentions > 0 THEN 'Fundraising'
        WHEN acquisition_mentions > 0 THEN 'M&A'
        ELSE 'General News'
    END as primary_activity
FROM workspace.news_monitoring.gold_company_mentions
WHERE mention_count >= 2
ORDER BY mention_count DESC
LIMIT 50;

-- ============================================================================
-- Query 5: Category Breakdown
-- Article distribution by category and region
SELECT
    category,
    region,
    article_count,
    ROUND(100.0 * article_count / SUM(article_count) OVER (PARTITION BY region), 1) as pct_of_region
FROM workspace.news_monitoring.gold_category_analysis
ORDER BY region, article_count DESC;

-- ============================================================================
-- Query 6: Funding by Round Type
-- Aggregate funding by stage (Seed, Series A/B/C, etc.)
SELECT
    funding_round,
    COUNT(*) as deal_count,
    SUM(funding_amount_millions) as total_millions,
    ROUND(AVG(funding_amount_millions), 2) as avg_deal_size_millions,
    region
FROM workspace.news_monitoring.gold_funding_tracker
WHERE funding_round IS NOT NULL
GROUP BY funding_round, region
ORDER BY region, total_millions DESC;

-- ============================================================================
-- Query 7: Source Performance
-- Article counts and quality metrics by source
SELECT
    source,
    region,
    SUM(total_articles) as total_articles,
    SUM(funding_articles) as funding_articles,
    SUM(acquisition_articles) as acquisition_articles,
    MAX(ingestion_date) as latest_data
FROM workspace.news_monitoring.gold_daily_activity
GROUP BY source, region
ORDER BY total_articles DESC;

-- ============================================================================
-- Query 8: Hiring vs Layoffs Trend
-- Job market health indicator
SELECT
    ingestion_date,
    region,
    SUM(hiring_articles) as hiring_news,
    SUM(layoff_articles) as layoff_news,
    SUM(hiring_articles) - SUM(layoff_articles) as net_hiring_sentiment
FROM workspace.news_monitoring.gold_daily_activity
GROUP BY ingestion_date, region
ORDER BY ingestion_date DESC;

-- ============================================================================
-- Query 9: Recent High-Value Deals (>$10M)
-- Major funding announcements
SELECT
    title,
    funding_round,
    funding_amount_millions,
    region,
    mentioned_companies,
    url,
    DATE(published_date) as date
FROM workspace.news_monitoring.gold_funding_tracker
WHERE funding_amount_millions >= 10
ORDER BY funding_amount_millions DESC, published_date DESC
LIMIT 25;

-- ============================================================================
-- Query 10: Weekly Summary Stats
-- Key metrics for the past week
WITH weekly_stats AS (
    SELECT
        COUNT(*) as total_articles,
        SUM(CASE WHEN has_funding THEN 1 ELSE 0 END) as funding_count,
        SUM(CASE WHEN has_acquisition THEN 1 ELSE 0 END) as acquisition_count,
        SUM(funding_amount_usd) / 1000000 as total_funding_millions,
        region
    FROM workspace.news_monitoring.silver_articles
    WHERE ingestion_date >= CURRENT_DATE - INTERVAL 7 DAYS
    GROUP BY region
)
SELECT
    region,
    total_articles,
    funding_count,
    acquisition_count,
    ROUND(total_funding_millions, 2) as funding_millions,
    ROUND(total_funding_millions / NULLIF(funding_count, 0), 2) as avg_deal_size_millions
FROM weekly_stats
ORDER BY total_articles DESC;

-- ============================================================================
-- Query 11: Content Freshness
-- Data quality check - how recent is our data?
SELECT
    source,
    region,
    MAX(ingestion_date) as latest_ingestion,
    COUNT(*) as total_articles,
    DATEDIFF(CURRENT_DATE, MAX(ingestion_date)) as days_since_update
FROM workspace.news_monitoring.raw_news_articles
GROUP BY source, region
ORDER BY days_since_update, source;

-- ============================================================================
-- Query 12: Top Headlines - Most Relevant
-- Recent articles with high signal (funding or M&A)
SELECT
    title,
    source,
    region,
    CASE
        WHEN has_funding AND has_acquisition THEN 'Funding + M&A'
        WHEN has_funding THEN 'Funding'
        WHEN has_acquisition THEN 'Acquisition'
        ELSE 'Other'
    END as news_type,
    funding_round,
    funding_amount_usd / 1000000 as amount_millions,
    url,
    DATE(published_date) as date
FROM workspace.news_monitoring.silver_articles
WHERE (has_funding OR has_acquisition)
  AND published_date >= CURRENT_DATE - INTERVAL 7 DAYS
ORDER BY published_date DESC
LIMIT 30;
