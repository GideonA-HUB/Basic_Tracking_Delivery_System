#!/usr/bin/env python
"""
Force MarketAux API fetch - bypasses startup timing issues
"""
import os
import sys
import django
import requests
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

def force_marketaux_fetch():
    """Force fetch MarketAux API with direct environment variable access"""
    print("🚀 FORCE MARKETAUX API FETCH")
    print("=" * 60)
    
    # Check environment variables directly
    print("🔍 CHECKING ENVIRONMENT VARIABLES DIRECTLY...")
    marketaux_key = os.environ.get('MARKETAUX_API_KEY')
    print(f"MARKETAUX_API_KEY: {'✅ Set' if marketaux_key else '❌ Not Set'}")
    
    if marketaux_key:
        print(f"Key length: {len(marketaux_key)}")
        print(f"Key preview: {marketaux_key[:8]}...")
        print(f"Key ends with: ...{marketaux_key[-4:]}")
    else:
        print("❌ No MarketAux API key found in environment variables!")
        return False
    
    # Test API call directly
    print(f"\n🌐 TESTING MARKETAUX API DIRECTLY...")
    try:
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            'api_token': marketaux_key,
            'symbols': 'BTC,ETH,AAPL,MSFT,GOOGL,TSLA',
            'limit': 20,
            'language': 'en',
            'filter_entities': 'true'
        }
        
        print(f"Making API request...")
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('data', [])
            print(f"✅ API Success: {len(articles)} articles returned")
            
            if articles:
                print(f"\n📰 SAMPLE ARTICLES:")
                for i, article in enumerate(articles[:5]):
                    print(f"  {i+1}. {article.get('title', 'No title')[:60]}...")
                    print(f"     Source: {article.get('source', 'Unknown')}")
                    print(f"     Published: {article.get('published_at', 'Unknown')}")
                    print()
                
                return articles
            else:
                print("No articles in response")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error message: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ API Exception: {e}")
        return False

def save_articles_to_database(articles):
    """Save articles to database using Django ORM"""
    print(f"\n💾 SAVING ARTICLES TO DATABASE...")
    
    try:
        # Set up Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
        django.setup()
        
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
        for article_data in articles:
            try:
                # Determine category based on symbols or content
                category_name = 'crypto'  # Default
                symbols = article_data.get('entities', [])
                if symbols:
                    symbol_names = [s.get('symbol', '') for s in symbols]
                    if any(s in ['BTC', 'ETH', 'ADA', 'SOL'] for s in symbol_names):
                        category_name = 'crypto'
                    elif any(s in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'] for s in symbol_names):
                        category_name = 'stocks'
                    elif any(s in ['REIT', 'SPG', 'PLD'] for s in symbol_names):
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
                    is_featured=saved_count < 5,  # First 5 are featured
                    is_active=True,
                    tags=','.join([s.get('symbol', '') for s in symbols[:5]])
                )
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving article: {e}")
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
    """Main function"""
    print("🚀 FORCE MARKETAUX API FETCH - BYPASSING STARTUP TIMING ISSUES")
    print("=" * 80)
    
    # Force fetch from API
    articles = force_marketaux_fetch()
    
    if articles:
        print(f"\n🎉 SUCCESS! Fetched {len(articles)} articles from MarketAux API")
        
        # Save to database
        if save_articles_to_database(articles):
            print(f"\n✅ COMPLETE SUCCESS! MarketAux API is working and articles are saved!")
        else:
            print(f"\n❌ Failed to save articles to database")
    else:
        print(f"\n❌ Failed to fetch articles from MarketAux API")
    
    print("\n" + "=" * 80)
    print("Force fetch completed!")

if __name__ == "__main__":
    main()
