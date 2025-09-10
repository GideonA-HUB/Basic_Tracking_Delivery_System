#!/usr/bin/env python
"""
Guaranteed startup script with force MarketAux fetch
This script ensures MarketAux API is called regardless of timing issues
"""
import os
import sys
import django
import subprocess
import threading
import time
from django.core.management import execute_from_command_line

def force_fetch_marketaux_news():
    """Force fetch MarketAux news with direct environment access"""
    print("🚀 FORCE FETCHING MARKETAUX NEWS - GUARANTEED METHOD")
    print("=" * 60)
    
    # Get API key directly from environment
    marketaux_key = os.environ.get('MARKETAUX_API_KEY')
    print(f"MARKETAUX_API_KEY: {'✅ Set' if marketaux_key else '❌ Not Set'}")
    
    if not marketaux_key:
        print("❌ No MarketAux API key found in environment variables!")
        return False
    
    print(f"Key length: {len(marketaux_key)}")
    print(f"Key preview: {marketaux_key[:8]}...")
    
    # Test API call directly
    try:
        import requests
        
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            'api_token': marketaux_key,
            'symbols': 'BTC,ETH,AAPL,MSFT,GOOGL,TSLA,AMZN,META,NVDA,AMD',
            'limit': 30,
            'language': 'en',
            'filter_entities': 'true'
        }
        
        print(f"Making API request to MarketAux...")
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('data', [])
            print(f"✅ API Success: {len(articles)} articles returned")
            
            if articles:
                # Save to database
                return save_articles_to_database(articles)
            else:
                print("No articles in response")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ API Exception: {e}")
        return False

def save_articles_to_database(articles):
    """Save articles to database"""
    try:
        from investments.news_models import NewsArticle, NewsCategory, NewsSource
        from django.utils import timezone
        from datetime import datetime
        
        # Clear existing articles
        NewsArticle.objects.all().delete()
        print("🗑️  Cleared existing articles")
        
        # Create categories
        categories = {
            'crypto': NewsCategory.objects.get_or_create(
                name='crypto',
                defaults={'display_name': 'Cryptocurrency', 'description': 'Crypto news'}
            )[0],
            'stocks': NewsCategory.objects.get_or_create(
                name='stocks',
                defaults={'display_name': 'Stock Market', 'description': 'Stock news'}
            )[0],
            'real_estate': NewsCategory.objects.get_or_create(
                name='real_estate',
                defaults={'display_name': 'Real Estate', 'description': 'Real estate news'}
            )[0],
            'bitcoin': NewsCategory.objects.get_or_create(
                name='bitcoin',
                defaults={'display_name': 'Bitcoin', 'description': 'Bitcoin news'}
            )[0],
            'ethereum': NewsCategory.objects.get_or_create(
                name='ethereum',
                defaults={'display_name': 'Ethereum', 'description': 'Ethereum news'}
            )[0],
            'altcoins': NewsCategory.objects.get_or_create(
                name='altcoins',
                defaults={'display_name': 'Altcoins', 'description': 'Altcoin news'}
            )[0],
        }
        
        # Create source
        source, _ = NewsSource.objects.get_or_create(
            name='MarketAux',
            defaults={
                'base_url': 'https://api.marketaux.com',
                'is_active': True
            }
        )
        
        # Save articles
        saved_count = 0
        for i, article_data in enumerate(articles):
            try:
                # Determine category based on symbols
                category_name = 'crypto'  # Default
                symbols = article_data.get('entities', [])
                if symbols:
                    symbol_names = [s.get('symbol', '') for s in symbols]
                    if any(s in ['BTC', 'ETH', 'ADA', 'SOL', 'MATIC', 'AVAX'] for s in symbol_names):
                        category_name = 'crypto'
                    elif any(s in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA'] for s in symbol_names):
                        category_name = 'stocks'
                    elif any(s in ['REIT', 'SPG', 'PLD', 'AMT'] for s in symbol_names):
                        category_name = 'real_estate'
                
                # Parse published date
                published_at = timezone.now()
                if article_data.get('published_at'):
                    try:
                        published_at = datetime.fromisoformat(
                            article_data['published_at'].replace('Z', '+00:00')
                        )
                    except:
                        published_at = timezone.now()
                
                # Create article
                article = NewsArticle.objects.create(
                    title=article_data.get('title', ''),
                    summary=article_data.get('description', ''),
                    content=article_data.get('description', ''),
                    url=article_data.get('url', ''),
                    image_url=article_data.get('image_url', '/static/images/news-placeholder.svg'),
                    published_at=published_at,
                    source=source,
                    category=categories[category_name],
                    is_featured=i < 5,  # First 5 are featured
                    is_active=True,
                    tags=','.join([s.get('symbol', '') for s in symbols[:5]])
                )
                saved_count += 1
                
                if i < 3:  # Show first 3 articles
                    print(f"  {i+1}. {article.title[:50]}...")
                
            except Exception as e:
                print(f"Error saving article {i+1}: {e}")
                continue
        
        print(f"✅ Saved {saved_count} articles to database")
        
        # Show final stats
        total_articles = NewsArticle.objects.count()
        featured_articles = NewsArticle.objects.filter(is_featured=True).count()
        active_articles = NewsArticle.objects.filter(is_active=True).count()
        
        print(f"📊 FINAL STATS: {total_articles} total, {featured_articles} featured, {active_articles} active")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    # Initialize Django
    django.setup()
    
    print("🚀 STARTING APPLICATION WITH GUARANTEED MARKETAUX FETCH")
    print("=" * 80)
    
    try:
        # Run migrations first
        print("🔄 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations completed successfully")
        
        # Collect static files
        print("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected successfully")
        
        # FORCE FETCH MARKETAUX NEWS
        print("🚀 FORCE FETCHING MARKETAUX NEWS...")
        success = force_fetch_marketaux_news()
        
        if success:
            print("🎉 SUCCESS! MarketAux API is working and articles are saved!")
        else:
            print("⚠️ MarketAux fetch failed, but continuing with server startup...")
        
        # Start the server
        print("🚀 Starting Daphne server...")
        
        # Get port from environment
        port = os.environ.get('PORT', '8080')
        
        # Start Daphne
        cmd = [
            'daphne', 
            '-b', '0.0.0.0', 
            '-p', port, 
            'delivery_tracker.asgi:application'
        ]
        
        print(f"🚀 Starting server on port {port}")
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
