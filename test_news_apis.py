#!/usr/bin/env python
"""
Test script to debug news API calls and force them to work
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.conf import settings
from investments.news_services import NewsAPIService, FinnhubService, CryptoPanicService, CoinDeskService, NewsAggregator
import requests
import json

def test_api_keys():
    """Test if API keys are loaded correctly"""
    print("🔑 TESTING API KEYS LOADING...")
    print(f"NEWSAPI_KEY: {'✅ Set' if settings.NEWSAPI_KEY else '❌ Not Set'}")
    print(f"FINNHUB_API_KEY: {'✅ Set' if settings.FINNHUB_API_KEY else '❌ Not Set'}")
    print(f"CRYPTOPANIC_API_KEY: {'✅ Set' if settings.CRYPTOPANIC_API_KEY else '❌ Not Set'}")
    print(f"COINDESK_API_KEY: {'✅ Set' if settings.COINDESK_API_KEY else '❌ Not Set'}")
    
    if settings.NEWSAPI_KEY:
        print(f"NewsAPI Key length: {len(settings.NEWSAPI_KEY)}")
        print(f"NewsAPI Key preview: {settings.NEWSAPI_KEY[:8]}...")
    
    if settings.FINNHUB_API_KEY:
        print(f"Finnhub Key length: {len(settings.FINNHUB_API_KEY)}")
        print(f"Finnhub Key preview: {settings.FINNHUB_API_KEY[:8]}...")

def test_newsapi_direct():
    """Test NewsAPI directly with requests"""
    print("\n🌐 TESTING NEWSAPI DIRECTLY...")
    
    if not settings.NEWSAPI_KEY:
        print("❌ NewsAPI key not available")
        return
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={settings.NEWSAPI_KEY}"
        print(f"Making request to: {url[:50]}...")
        
        response = requests.get(url, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Articles found: {len(data.get('articles', []))}")
            if data.get('articles'):
                print(f"First article title: {data['articles'][0].get('title', 'No title')}")
            else:
                print("No articles in response")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing NewsAPI: {e}")

def test_finnhub_direct():
    """Test Finnhub directly with requests"""
    print("\n🌐 TESTING FINNHUB DIRECTLY...")
    
    if not settings.FINNHUB_API_KEY:
        print("❌ Finnhub key not available")
        return
    
    try:
        url = f"https://finnhub.io/api/v1/news?category=general&token={settings.FINNHUB_API_KEY}"
        print(f"Making request to: {url[:50]}...")
        
        response = requests.get(url, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Articles found: {len(data) if isinstance(data, list) else 'Not a list'}")
            if isinstance(data, list) and data:
                print(f"First article title: {data[0].get('headline', 'No title')}")
            else:
                print("No articles in response")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing Finnhub: {e}")

def test_services():
    """Test the service classes"""
    print("\n🔧 TESTING SERVICE CLASSES...")
    
    # Test NewsAPI Service
    print("\n--- NewsAPI Service ---")
    newsapi = NewsAPIService()
    print(f"Is configured: {newsapi.is_configured}")
    if newsapi.is_configured:
        articles = newsapi.fetch_news('business', 5)
        print(f"Articles fetched: {len(articles)}")
        if articles:
            print(f"First article: {articles[0].get('title', 'No title')}")
    
    # Test Finnhub Service
    print("\n--- Finnhub Service ---")
    finnhub = FinnhubService()
    print(f"Is configured: {finnhub.is_configured}")
    if finnhub.is_configured:
        articles = finnhub.fetch_news('stocks', 5)
        print(f"Articles fetched: {len(articles)}")
        if articles:
            print(f"First article: {articles[0].get('title', 'No title')}")

def test_aggregator():
    """Test the news aggregator"""
    print("\n🔄 TESTING NEWS AGGREGATOR...")
    
    aggregator = NewsAggregator()
    configured = aggregator.get_configured_services()
    print(f"Configured services: {configured}")
    
    if configured:
        print("Attempting to fetch news...")
        articles = aggregator.fetch_all_news(['crypto', 'stocks'], 5)
        print(f"Total articles fetched: {len(articles)}")
        
        if articles:
            print("Sample articles:")
            for i, article in enumerate(articles[:3]):
                print(f"  {i+1}. {article.get('title', 'No title')}")
    else:
        print("❌ No services configured")

def force_create_news():
    """Force create news articles if APIs fail"""
    print("\n🚨 FORCING NEWS CREATION...")
    
    try:
        from investments.news_models import NewsArticle, NewsCategory, NewsSource
        from django.utils import timezone
        
        # Clear existing news
        NewsArticle.objects.all().delete()
        print("🗑️  Cleared existing news")
        
        # Create categories
        crypto_cat, _ = NewsCategory.objects.get_or_create(
            name='crypto',
            defaults={'display_name': 'Cryptocurrency', 'description': 'Crypto news'}
        )
        
        # Create source
        source, _ = NewsSource.objects.get_or_create(
            name='Test News',
            defaults={'base_url': 'https://test.com', 'is_active': True}
        )
        
        # Create test articles
        test_articles = [
            {
                'title': 'Bitcoin Surges to New All-Time High',
                'summary': 'Bitcoin has reached unprecedented levels as institutional adoption continues to grow.',
                'category': crypto_cat,
                'is_featured': True
            },
            {
                'title': 'Stock Market Shows Strong Performance',
                'summary': 'Major indices are up as technology companies report strong earnings.',
                'category': crypto_cat,
                'is_featured': False
            }
        ]
        
        created_count = 0
        for article_data in test_articles:
            NewsArticle.objects.create(
                title=article_data['title'],
                summary=article_data['summary'],
                content=article_data['summary'],
                source=source,
                category=article_data['category'],
                is_featured=article_data['is_featured'],
                is_active=True,
                published_at=timezone.now()
            )
            created_count += 1
        
        print(f"✅ Created {created_count} test articles")
        
        # Show final count
        total = NewsArticle.objects.count()
        print(f"📊 Total articles in database: {total}")
        
    except Exception as e:
        print(f"❌ Error creating test news: {e}")

if __name__ == "__main__":
    print("🚀 STARTING NEWS API DEBUG TEST...")
    
    test_api_keys()
    test_newsapi_direct()
    test_finnhub_direct()
    test_services()
    test_aggregator()
    
    # If no articles were created, force create some
    from investments.news_models import NewsArticle
    if NewsArticle.objects.count() == 0:
        print("\n⚠️  No articles found, forcing creation...")
        force_create_news()
    
    print("\n✅ DEBUG TEST COMPLETE!")
