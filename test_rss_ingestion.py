"""Test script to fetch RSS feeds and display results."""

import sys
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_sources.rss_parser import fetch_all_feeds
from utils.config_loader import get_config_loader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Fetch RSS feeds and display results."""
    print("=" * 80)
    print("RSS FEED INGESTION TEST")
    print("=" * 80)
    print()

    # Load configuration
    print("Loading configuration...")
    config_loader = get_config_loader()
    config = config_loader.load()
    print("✓ Configuration loaded")
    print()

    # Fetch all feeds
    print("Fetching RSS feeds...")
    print("-" * 80)
    articles = fetch_all_feeds(config)
    print("-" * 80)
    print()

    # Display summary
    print("=" * 80)
    print(f"SUMMARY: Fetched {len(articles)} articles")
    print("=" * 80)
    print()

    # Group by source
    by_source = {}
    by_region = {}

    for article in articles:
        source = article['source']
        region = article['region']

        by_source[source] = by_source.get(source, 0) + 1
        by_region[region] = by_region.get(region, 0) + 1

    print("Articles by Source:")
    for source, count in sorted(by_source.items()):
        print(f"  {source:20s}: {count:3d} articles")
    print()

    print("Articles by Region:")
    for region, count in sorted(by_region.items()):
        print(f"  {region:20s}: {count:3d} articles")
    print()

    # Display sample articles
    print("=" * 80)
    print("SAMPLE ARTICLES (first 3)")
    print("=" * 80)
    print()

    for i, article in enumerate(articles[:3], 1):
        print(f"Article {i}:")
        print(f"  Source:    {article['source']}")
        print(f"  Region:    {article['region']}")
        print(f"  Title:     {article['title'][:70]}...")
        print(f"  URL:       {article['url']}")
        print(f"  Published: {article['published_date']}")
        print(f"  Author:    {article['author']}")
        print(f"  Categories: {', '.join(article['categories'][:3])}")
        print()

    # Save to JSON file
    output_file = Path(__file__).parent / 'data' / 'sample_rss_output.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Saving results to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved {len(articles)} articles to {output_file}")
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
