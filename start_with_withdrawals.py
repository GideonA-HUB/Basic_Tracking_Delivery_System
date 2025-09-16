#!/usr/bin/env python
"""
Railway startup script with withdrawal data population
This script ensures withdrawal data is available on deployment
"""
import os
import sys
import django
import subprocess
import threading
import time
from django.core.management import execute_from_command_line

def populate_withdrawal_data():
    """Populate withdrawal data for production"""
    print("🚀 POPULATING WITHDRAWAL DATA FOR PRODUCTION")
    print("=" * 60)
    
    try:
        # Check if we already have withdrawal data
        from investments.models import CryptoWithdrawal
        existing_count = CryptoWithdrawal.objects.count()
        
        if existing_count > 0:
            print(f"✅ Withdrawal data already exists: {existing_count} records")
            # Ensure Margaret Kneeland is added
            ensure_margaret_kneeland()
            return True
        
        print("📊 No withdrawal data found, populating sample data...")
        
        # Run the populate_withdrawals command
        execute_from_command_line(['manage.py', 'populate_withdrawals'])
        
        # Ensure Margaret Kneeland is added
        ensure_margaret_kneeland()
        
        # Verify data was created
        new_count = CryptoWithdrawal.objects.count()
        print(f"✅ Successfully populated {new_count} withdrawal records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating withdrawal data: {e}")
        import traceback
        traceback.print_exc()
        return False

def ensure_margaret_kneeland():
    """Ensure Margaret Kneeland is in the withdrawal list"""
    print("🔍 ENSURING MARGARET KNEELAND IS IN WITHDRAWAL LIST")
    print("=" * 60)
    
    try:
        from investments.models import CryptoWithdrawal
        from datetime import datetime, timedelta
        
        # Check if Margaret Kneeland already exists
        existing = CryptoWithdrawal.objects.filter(name="Margaret Kneeland").first()
        if existing:
            print(f"✅ Margaret Kneeland already exists: ${existing.amount:,.2f} - {existing.status}")
            return True
        
        # Get the current count to set order position
        current_count = CryptoWithdrawal.objects.count()
        order_position = current_count + 1  # Add at the end
        
        # Calculate estimated delivery date (3 weeks from now) - ensure timezone-aware
        from django.utils import timezone
        estimated_delivery = timezone.now() + timedelta(weeks=3)
        
        # Create the new withdrawal entry
        withdrawal = CryptoWithdrawal.objects.create(
            name="Margaret Kneeland",
            amount=224490.00,
            status='pending',
            priority='normal',
            estimated_delivery=estimated_delivery,
            order_position=order_position,
            is_public=True,
            notes='Added via startup script - 3 weeks estimated delivery'
        )
        
        print(f"✅ Successfully added Margaret Kneeland to withdrawal list")
        print(f"   Name: {withdrawal.name}")
        print(f"   Amount: ${withdrawal.amount:,.2f}")
        print(f"   Status: {withdrawal.status}")
        print(f"   Estimated Delivery: {withdrawal.estimated_delivery_display}")
        print(f"   Total Withdrawals: {CryptoWithdrawal.objects.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding Margaret Kneeland: {e}")
        import traceback
        traceback.print_exc()
        return False

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
            
            url = "https://api.marketaux.com/v1/news/all"
            params = {
                'api_token': marketaux_key,
                'symbols': 'BTC,ETH,AAPL,MSFT,GOOGL,TSLA,AMZN,META,NVDA,AMD',
                'limit': 20,
                'language': 'en',
                'filter_entities': 'true'
            }
            
            print(f"Making API request to MarketAux...")
            response = requests.get(url, params=params, timeout=30)
            
            print(f"MarketAux Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('data', [])
                print(f"✅ MarketAux Success: {len(articles)} articles returned")
                
                # Add source info to articles
                for article in articles:
                    article['source'] = 'MarketAux'
                all_articles.extend(articles)
            else:
                print(f"❌ MarketAux Error: {response.status_code}")
                print(f"Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ MarketAux Exception: {e}")
    
    # Test CryptoNewsAPI
    if cryptonews_key:
        try:
            import requests
            
            url = "https://cryptonewsapi.online/api/v1/news"
            params = {
                'tickers': 'BTC,ETH,ADA,SOL,MATIC,AVAX',
                'items': 20
            }
            headers = {
                'X-API-Key': cryptonews_key
            }
            
            print(f"Making API request to CryptoNewsAPI...")
            print(f"URL: {url}")
            print(f"Params: {params}")
            print(f"Headers: X-API-Key: {cryptonews_key[:8]}...")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            print(f"CryptoNews Response Status: {response.status_code}")
            print(f"CryptoNews Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"CryptoNews Raw Response: {data}")
                articles = data.get('data', {}).get('articles', [])
                print(f"✅ CryptoNews Success: {len(articles)} articles returned")
                
                if articles:
                    # Convert CryptoNewsAPI format to our standard format
                    for article in articles:
                        formatted_article = {
                            'title': article.get('title', ''),
                            'summary': article.get('description', ''),
                            'content': article.get('description', ''),
                            'url': article.get('link', ''),
                            'image_url': '/static/images/news-placeholder.svg',
                            'published_at': article.get('pubDate', ''),
                            'source': 'CryptoNewsAPI',
                            'category': 'crypto',
                            'symbols': 'BTC,ETH'  # Default crypto symbols
                        }
                        all_articles.append(formatted_article)
                else:
                    print("No articles in CryptoNews response - checking response structure...")
                    print(f"Response keys: {list(data.keys())}")
            else:
                print(f"❌ CryptoNews Error: {response.status_code}")
                print(f"Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ CryptoNews Exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Test Finnhub API
    if finnhub_key:
        try:
            import requests
            
            # Test both general and crypto categories
            for category in ['general', 'crypto']:
                url = f"https://finnhub.io/api/v1/news"
                params = {
                    'category': category,
                    'token': finnhub_key
                }
                
                print(f"Making API request to Finnhub ({category})...")
                print(f"URL: {url}")
                print(f"Params: {params}")
                response = requests.get(url, params=params, timeout=30)
                
                print(f"Finnhub ({category}) Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Finnhub ({category}) Raw Response: {data[:2] if data else 'Empty'}")
                    articles = data if isinstance(data, list) else []
                    print(f"✅ Finnhub ({category}) Success: {len(articles)} articles returned")
                    
                    if articles:
                        # Add source info to articles
                        for article in articles:
                            article['source'] = 'Finnhub'
                            article['category'] = category
                        all_articles.extend(articles)
                    else:
                        print(f"No articles in Finnhub ({category}) response")
                else:
                    print(f"❌ Finnhub ({category}) Error: {response.status_code}")
                    print(f"Error: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"❌ Finnhub Exception: {e}")
            import traceback
            traceback.print_exc()
    
    if all_articles:
        print(f"✅ Total articles from all APIs: {len(all_articles)}")
        # Save to database
        return save_articles_to_database(all_articles)
    else:
        print("❌ No articles from any API")
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
                source_name = article_data.get('source', 'Unknown')
                
                # Handle different API formats
                if source_name == 'MarketAux':
                    # MarketAux format
                    symbols = article_data.get('entities', [])
                    symbol_names = [s.get('symbol', '') for s in symbols] if symbols else []
                    title = article_data.get('title', '')
                    summary = article_data.get('description', '')
                    content = article_data.get('description', '')
                    url = article_data.get('url', '')
                    image_url = article_data.get('image_url', '/static/images/news-placeholder.svg')
                    published_at_str = article_data.get('published_at', '')
                    
                elif source_name == 'CryptoNewsAPI':
                    # CryptoNewsAPI format
                    tickers = article_data.get('tickers', [])
                    symbol_names = tickers if tickers else []
                    title = article_data.get('title', '')
                    summary = article_data.get('text', '')
                    content = article_data.get('text', '')
                    url = article_data.get('news_url', '')
                    image_url = article_data.get('image_url', '/static/images/news-placeholder.svg')
                    published_at_str = article_data.get('date', '')
                    
                elif source_name == 'Finnhub':
                    # Finnhub format
                    related = article_data.get('related', '')
                    symbol_names = [related] if related else []
                    title = article_data.get('headline', '')
                    summary = article_data.get('summary', '')
                    content = article_data.get('summary', '')
                    url = article_data.get('url', '')
                    image_url = article_data.get('image', '/static/images/news-placeholder.svg')
                    published_at_str = article_data.get('datetime', '')
                    
                else:
                    # Default format
                    symbols = article_data.get('entities', [])
                    symbol_names = [s.get('symbol', '') for s in symbols] if symbols else []
                    title = article_data.get('title', '')
                    summary = article_data.get('description', '')
                    content = article_data.get('description', '')
                    url = article_data.get('url', '')
                    image_url = article_data.get('image_url', '/static/images/news-placeholder.svg')
                    published_at_str = article_data.get('published_at', '')
                
                # Determine category based on symbols
                category_name = 'crypto'  # Default
                if symbol_names:
                    if any(s in ['BTC'] for s in symbol_names):
                        category_name = 'bitcoin'
                    elif any(s in ['ETH'] for s in symbol_names):
                        category_name = 'ethereum'
                    elif any(s in ['ADA', 'SOL', 'MATIC', 'AVAX', 'DOT', 'LINK', 'UNI', 'AAVE'] for s in symbol_names):
                        category_name = 'altcoins'
                    elif any(s in ['BTC', 'ETH', 'ADA', 'SOL', 'MATIC', 'AVAX'] for s in symbol_names):
                        category_name = 'crypto'
                    elif any(s in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA'] for s in symbol_names):
                        category_name = 'stocks'
                    elif any(s in ['REIT', 'SPG', 'PLD', 'AMT'] for s in symbol_names):
                        category_name = 'real_estate'
                
                # Parse published date
                published_at = timezone.now()
                if published_at_str:
                    try:
                        published_at = datetime.fromisoformat(
                            published_at_str.replace('Z', '+00:00')
                        )
                    except:
                        published_at = timezone.now()
                
                # Get or create source
                base_url_map = {
                    'MarketAux': 'https://api.marketaux.com',
                    'CryptoNewsAPI': 'https://cryptonewsapi.online',
                    'Finnhub': 'https://finnhub.io'
                }
                
                source, _ = NewsSource.objects.get_or_create(
                    name=source_name,
                    defaults={
                        'base_url': base_url_map.get(source_name, 'https://unknown.com'),
                        'is_active': True
                    }
                )
                
                # Truncate fields before database operation
                title = title[:200] if title else ''
                summary = summary[:500] if summary else ''
                content = content[:1000] if content else ''
                url = url[:500] if url else ''
                image_url = image_url[:500] if image_url else '/static/images/news-placeholder.svg'
                tags = ','.join(symbol_names[:5])[:200] if symbol_names else ''
                
                # Create article
                article = NewsArticle.objects.create(
                    title=title,
                    summary=summary,
                    content=content,
                    url=url,
                    image_url=image_url,
                    published_at=published_at,
                    source=source,
                    category=categories[category_name],
                    is_featured=i < 5,  # First 5 are featured
                    is_active=True,
                    tags=tags
                )
                saved_count += 1
                
                if i < 3:  # Show first 3 articles
                    print(f"  {i+1}. {article.title[:50]}... ({source_name})")
                
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
    
    print("🚀 STARTING APPLICATION WITH WITHDRAWAL DATA & NEWS")
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
        
        # POPULATE WITHDRAWAL DATA
        print("🚀 POPULATING WITHDRAWAL DATA...")
        withdrawal_success = populate_withdrawal_data()
        
        if withdrawal_success:
            print("🎉 SUCCESS! Withdrawal data is populated!")
        else:
            print("⚠️ Withdrawal data population failed, but continuing...")
        
        # FORCE FETCH MARKETAUX NEWS
        print("🚀 FORCE FETCHING MARKETAUX NEWS...")
        news_success = force_fetch_marketaux_news()
        
        if news_success:
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
