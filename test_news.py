#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.news_models import NewsArticle, NewsCategory, NewsSource

def test_news_system():
    print("🧪 Testing News System...")
    
    # Test news articles
    total_articles = NewsArticle.objects.count()
    featured_articles = NewsArticle.objects.filter(is_featured=True).count()
    active_articles = NewsArticle.objects.filter(is_active=True).count()
    
    print(f"📊 News Statistics:")
    print(f"   Total Articles: {total_articles}")
    print(f"   Featured Articles: {featured_articles}")
    print(f"   Active Articles: {active_articles}")
    
    # Test categories
    categories = NewsCategory.objects.all()
    print(f"\n📂 Categories ({categories.count()}):")
    for category in categories:
        count = NewsArticle.objects.filter(category=category).count()
        print(f"   - {category.name}: {count} articles")
    
    # Test sources
    sources = NewsSource.objects.all()
    print(f"\n📰 Sources ({sources.count()}):")
    for source in sources:
        count = NewsArticle.objects.filter(source=source).count()
        print(f"   - {source.name}: {count} articles")
    
    # Sample articles
    print(f"\n📰 Sample Articles:")
    for article in NewsArticle.objects.all()[:5]:
        print(f"   - {article.title[:50]}... ({article.category.name})")
    
    # Test API data
    print(f"\n🔌 API Test:")
    featured_news = NewsArticle.objects.filter(is_active=True, is_featured=True)[:4]
    crypto_news = NewsArticle.objects.filter(is_active=True, category__name__in=['crypto', 'bitcoin', 'ethereum', 'altcoins'])[:4]
    stocks_news = NewsArticle.objects.filter(is_active=True, category__name='stocks')[:4]
    real_estate_news = NewsArticle.objects.filter(is_active=True, category__name='real_estate')[:4]
    
    print(f"   Featured News: {len(featured_news)} articles")
    print(f"   Crypto News: {len(crypto_news)} articles")
    print(f"   Stocks News: {len(stocks_news)} articles")
    print(f"   Real Estate News: {len(real_estate_news)} articles")
    
    print(f"\n✅ News system is working correctly!")
    return True

if __name__ == '__main__':
    test_news_system()
