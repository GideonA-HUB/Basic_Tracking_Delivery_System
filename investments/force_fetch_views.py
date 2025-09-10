"""
Force fetch views for MarketAux API
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
import os
import json
from datetime import datetime
from django.utils import timezone

@csrf_exempt
@require_http_methods(["POST"])
def force_fetch_marketaux_news(request):
    """Force fetch MarketAux news via API endpoint"""
    try:
        # Get API key directly from environment
        marketaux_key = os.environ.get('MARKETAUX_API_KEY')
        
        if not marketaux_key:
            return JsonResponse({
                'success': False,
                'error': 'MarketAux API key not found in environment variables'
            })
        
        # Test API call
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            'api_token': marketaux_key,
            'symbols': 'BTC,ETH,AAPL,MSFT,GOOGL,TSLA,AMZN,META,NVDA,AMD',
            'limit': 30,
            'language': 'en',
            'filter_entities': 'true'
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('data', [])
            
            if articles:
                # Save to database
                saved_count = save_articles_to_database(articles)
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully fetched and saved {saved_count} articles',
                    'articles_count': len(articles),
                    'saved_count': saved_count
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No articles returned from MarketAux API'
                })
        else:
            return JsonResponse({
                'success': False,
                'error': f'MarketAux API error: {response.status_code} - {response.text[:200]}'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Exception: {str(e)}'
        })

def save_articles_to_database(articles):
    """Save articles to database"""
    try:
        from investments.news_models import NewsArticle, NewsCategory, NewsSource
        
        # Clear existing articles
        NewsArticle.objects.all().delete()
        
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
                
            except Exception as e:
                continue
        
        return saved_count
        
    except Exception as e:
        return 0
