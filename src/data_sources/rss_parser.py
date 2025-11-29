"""RSS feed parser for news monitoring."""

import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
import logging

logger = logging.getLogger(__name__)

# Browser User-Agent for feeds that require it
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


class RSSFeedParser:
    """Parse RSS feeds and extract structured article data."""

    def __init__(self, timeout: int = 30):
        """Initialize the RSS parser.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def fetch_feed(self, url: str, requires_user_agent: bool = False) -> feedparser.FeedParserDict:
        """Fetch and parse an RSS feed.

        Args:
            url: RSS feed URL
            requires_user_agent: Whether to use custom User-Agent header

        Returns:
            Parsed feed object

        Raises:
            Exception: If feed fetch fails
        """
        try:
            if requires_user_agent:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                feed = feedparser.parse(response.content)
            else:
                feed = feedparser.parse(url)

            if feed.bozo and hasattr(feed, 'bozo_exception'):
                logger.warning(f"Feed parsing warning for {url}: {feed.bozo_exception}")

            return feed

        except requests.RequestException as e:
            logger.error(f"Failed to fetch feed {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error parsing feed {url}: {str(e)}")
            raise

    def parse_entry(
        self,
        entry: Any,
        source_name: str,
        region: str = "global",
        countries: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Parse a single RSS feed entry into structured format.

        Args:
            entry: RSS feed entry object
            source_name: Name of the source feed
            region: Geographic region (sea, europe, global)
            countries: List of country codes

        Returns:
            Structured article dictionary
        """
        # Generate unique article ID from URL
        article_url = entry.get('link', '')
        article_id = hashlib.md5(article_url.encode()).hexdigest()

        # Parse publication date
        published_date = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                published_date = datetime(*entry.published_parsed[:6]).isoformat()
            except (TypeError, ValueError):
                pass

        if not published_date and hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            try:
                published_date = datetime(*entry.updated_parsed[:6]).isoformat()
            except (TypeError, ValueError):
                pass

        # Extract categories/tags
        categories = []
        if hasattr(entry, 'tags'):
            categories = [tag.get('term', '') for tag in entry.tags if tag.get('term')]

        # Extract author
        author = entry.get('author', '')
        if not author and hasattr(entry, 'authors') and entry.authors:
            author = entry.authors[0].get('name', '')

        # Extract content (prefer content over summary)
        content = ''
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].get('value', '')
        elif hasattr(entry, 'summary_detail'):
            content = entry.summary_detail.get('value', '')

        # Build structured article
        article = {
            'article_id': article_id,
            'source': source_name,
            'title': entry.get('title', ''),
            'description': entry.get('summary', ''),
            'content': content,
            'url': article_url,
            'author': author,
            'published_date': published_date,
            'categories': categories,
            'region': region,
            'country_codes': countries or [],
            'ingestion_timestamp': datetime.utcnow().isoformat(),
            'raw_data': dict(entry)  # Store original entry for reference
        }

        return article

    def parse_feed(
        self,
        url: str,
        source_name: str,
        region: str = "global",
        countries: Optional[List[str]] = None,
        requires_user_agent: bool = False,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Parse an RSS feed and extract all articles.

        Args:
            url: RSS feed URL
            source_name: Name of the source
            region: Geographic region
            countries: List of country codes
            requires_user_agent: Whether User-Agent header is required
            limit: Maximum number of articles to return

        Returns:
            List of structured article dictionaries
        """
        logger.info(f"Fetching feed: {source_name} ({url})")

        try:
            feed = self.fetch_feed(url, requires_user_agent)

            if not hasattr(feed, 'entries') or not feed.entries:
                logger.warning(f"No entries found in feed: {source_name}")
                return []

            articles = []
            entries = feed.entries[:limit] if limit else feed.entries

            for entry in entries:
                try:
                    article = self.parse_entry(entry, source_name, region, countries)
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Error parsing entry from {source_name}: {str(e)}")
                    continue

            logger.info(f"Parsed {len(articles)} articles from {source_name}")
            return articles

        except Exception as e:
            logger.error(f"Failed to parse feed {source_name}: {str(e)}")
            return []


def fetch_all_feeds(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Fetch articles from all configured RSS feeds.

    Args:
        config: Configuration dictionary with feed settings

    Returns:
        Combined list of articles from all feeds
    """
    parser = RSSFeedParser()
    all_articles = []

    rss_config = config.get('data_sources', {}).get('news_apis', [])
    rss_feeds = None

    # Find RSS feeds configuration
    for source in rss_config:
        if source.get('name') == 'rss_feeds' and source.get('enabled'):
            rss_feeds = source.get('feeds', [])
            break

    if not rss_feeds:
        logger.warning("No RSS feeds configured or enabled")
        return []

    for feed_config in rss_feeds:
        url = feed_config.get('url')
        name = feed_config.get('name', 'unknown')
        region = feed_config.get('region', 'global')
        countries = feed_config.get('countries', [])
        requires_ua = feed_config.get('requires_user_agent', False)

        if not url:
            logger.warning(f"Missing URL for feed: {name}")
            continue

        articles = parser.parse_feed(
            url=url,
            source_name=name,
            region=region,
            countries=countries,
            requires_user_agent=requires_ua
        )

        all_articles.extend(articles)

    logger.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles
