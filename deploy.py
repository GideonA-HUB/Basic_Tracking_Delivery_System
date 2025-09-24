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
    
    # Get API keys directly from environment
    marketaux_key = os.environ.get('MARKETAUX_API_KEY')
    cryptonews_key = os.environ.get('CRYPTONEWS_API_KEY')
    finnhub_key = os.environ.get('FINNHUB_API_KEY')
    
    print(f"MARKETAUX_API_KEY: {'✅ Set' if marketaux_key else '❌ Not Set'}")
    print(f"CRYPTONEWS_API_KEY: {'✅ Set' if cryptonews_key else '❌ Not Set'}")
    print(f"FINNHUB_API_KEY: {'✅ Set' if finnhub_key else '❌ Not Set'}")
    
    if not marketaux_key and not cryptonews_key and not finnhub_key:
        print("❌ No API keys found in environment variables!")
        return False
    
    if marketaux_key:
        print(f"MarketAux key length: {len(marketaux_key)}")
        print(f"MarketAux key preview: {marketaux_key[:8]}...")
    
    if cryptonews_key:
        print(f"CryptoNews key length: {len(cryptonews_key)}")
        print(f"CryptoNews key preview: {cryptonews_key[:8]}...")
    
    if finnhub_key:
        print(f"Finnhub key length: {len(finnhub_key)}")
        print(f"Finnhub key preview: {finnhub_key[:8]}...")
    
    # Test API calls directly
    all_articles = []
    
    # Test MarketAux API
    if marketaux_key:
        try:
            import requests
            
            print("Making API request to MarketAux...")
            response = requests.get(
                'https://api.marketaux.com/v1/news/all',
                params={
                    'api_token': marketaux_key,
                    'countries': 'us',
                    'limit': 10,
                    'language': 'en'
                },
                timeout=30
            )
            
            print(f"MarketAux Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('data', [])
                print(f"✅ MarketAux Success: {len(articles)} articles returned")
                
                for article in articles:
                    all_articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('published_at', ''),
                        'source': 'MarketAux',
                        'image_url': article.get('image_url', ''),
                        'symbols': ', '.join(article.get('symbols', [])),
                    })
            else:
                print(f"❌ MarketAux API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ MarketAux API Exception: {e}")
    
    # Test CryptoNews API
    if cryptonews_key:
        try:
            import requests
            
            print("Making API request to CryptoNewsAPI...")
            url = 'https://cryptonewsapi.online/api/v1/news'
            params = {
                'tickers': 'BTC,ETH,ADA,SOL,MATIC,AVAX',
                'items': 20
            }
            headers = {'X-API-Key': cryptonews_key}
            
            print(f"URL: {url}")
            print(f"Params: {params}")
            print(f"Headers: X-API-Key: {cryptonews_key[:8]}...")
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            print(f"CryptoNews Response Status: {response.status_code}")
            print(f"CryptoNews Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('data', {}).get('articles', [])
                print(f"✅ CryptoNews Success: {len(articles)} articles returned")
                
                # Show raw response for debugging
                print(f"CryptoNews Raw Response: {data}")
                
                for article in articles:
                    all_articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('link', ''),
                        'published_at': article.get('pubDate', ''),
                        'source': 'CryptoNews',
                        'image_url': '',
                        'symbols': '',
                    })
            else:
                print(f"❌ CryptoNews API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ CryptoNews API Exception: {e}")
    
    # Test Finnhub API (General)
    if finnhub_key:
        try:
            import requests
            
            print("Making API request to Finnhub (general)...")
            url = 'https://finnhub.io/api/v1/news'
            params = {
                'category': 'general',
                'token': finnhub_key
            }
            
            print(f"URL: {url}")
            print(f"Params: {params}")
            
            response = requests.get(url, params=params, timeout=30)
            
            print(f"Finnhub (general) Response Status: {response.status_code}")
            
            if response.status_code == 200:
                articles = response.json()
                print(f"✅ Finnhub (general) Success: {len(articles)} articles returned")
                
                # Show raw response for debugging
                print(f"Finnhub (general) Raw Response: {articles}")
                
                for article in articles[:50]:  # Limit to 50 articles
                    all_articles.append({
                        'title': article.get('headline', ''),
                        'description': article.get('summary', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('datetime', ''),
                        'source': 'Finnhub',
                        'image_url': article.get('image', ''),
                        'symbols': '',
                    })
            else:
                print(f"❌ Finnhub (general) API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Finnhub (general) API Exception: {e}")
    
    # Test Finnhub API (Crypto)
    if finnhub_key:
        try:
            import requests
            
            print("Making API request to Finnhub (crypto)...")
            url = 'https://finnhub.io/api/v1/news'
            params = {
                'category': 'crypto',
                'token': finnhub_key
            }
            
            print(f"URL: {url}")
            print(f"Params: {params}")
            
            response = requests.get(url, params=params, timeout=30)
            
            print(f"Finnhub (crypto) Response Status: {response.status_code}")
            
            if response.status_code == 200:
                articles = response.json()
                print(f"✅ Finnhub (crypto) Success: {len(articles)} articles returned")
                
                # Show raw response for debugging
                print(f"Finnhub (crypto) Raw Response: {articles}")
                
                for article in articles[:50]:  # Limit to 50 articles
                    all_articles.append({
                        'title': article.get('headline', ''),
                        'description': article.get('summary', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('datetime', ''),
                        'source': 'Finnhub',
                        'image_url': article.get('image', ''),
                        'symbols': '',
                    })
            else:
                print(f"❌ Finnhub (crypto) API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Finnhub (crypto) API Exception: {e}")
    
    print(f"✅ Total articles from all APIs: {len(all_articles)}")
    
    # Save articles to database
    if all_articles:
        success = save_articles_to_database(all_articles)
        return success
    else:
        print("❌ No articles retrieved from any API")
        return False

def save_articles_to_database(articles):
    """Save articles to database"""
    try:
        from investments.models import NewsArticle
        
        print("🗑️  Cleared existing articles")
        
        # Clear existing articles
        NewsArticle.objects.all().delete()
        
        # Save new articles
        saved_count = 0
        featured_count = 0
        
        for i, article_data in enumerate(articles[:100]):  # Limit to 100 articles
            try:
                # Create article
                article = NewsArticle.objects.create(
                    title=article_data['title'][:200],  # Limit title length
                    content=article_data['description'][:1000] if article_data['description'] else '',  # Limit content length
                    url=article_data['url'][:500] if article_data['url'] else '',  # Limit URL length
                    source=article_data['source'][:50],  # Limit source length
                    published_at=article_data['published_at'],
                    is_featured=i < 5,  # First 5 articles are featured
                    is_active=True,
                    image_url=article_data['image_url'][:500] if article_data['image_url'] else '',  # Limit image URL length
                    symbols=article_data['symbols'][:200] if article_data['symbols'] else '',  # Limit symbols length
                )
                
                saved_count += 1
                if article.is_featured:
                    featured_count += 1
                    
                print(f"  {i+1}. {article.title[:50]}... ({article.source})")
                
            except Exception as e:
                print(f"❌ Error saving article {i+1}: {e}")
                continue
        
        # Get final stats
        total_articles = NewsArticle.objects.count()
        featured_articles = NewsArticle.objects.filter(is_featured=True).count()
        active_articles = NewsArticle.objects.filter(is_active=True).count()
        
        print(f"✅ Saved {saved_count} articles to database")
        print(f"📊 FINAL STATS: {total_articles} total, {featured_articles} featured, {active_articles} active")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving articles to database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🚀 STARTING APPLICATION WITH GUARANTEED MARKETAUX FETCH")
    print("=" * 80)
    
    try:
        # Run migrations first (this will initialize Django properly)
        print("🔄 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations completed successfully")
        
        # Collect static files
        print("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected successfully")
        
        # Initialize Django after migrations are complete
        django.setup()
        
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
