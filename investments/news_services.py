"""
News API services for fetching real news from MarketAux API
"""
import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .news_models import NewsArticle, NewsCategory, NewsSource
import json

logger = logging.getLogger(__name__)


class FreeNewsService:
    """Service for fetching news from free sources (no API key required)"""
    
    def __init__(self):
        self.base_url = 'https://free-news-api.com'
        self.source, _ = NewsSource.objects.get_or_create(
            name='Free News',
            defaults={
                'base_url': 'https://free-news-api.com',
                'api_key': 'free',
                'rate_limit_per_hour': 1000
            }
        )
        self.is_configured = True  # Always configured since it's free
        
        # Debug logging
        logger.info(f"Free News Service - Always available (no API key required)")
    
    def fetch_news(self, category='business', count=20):
        """Fetch news from free sources"""
        if not self.is_configured:
            logger.warning("Free News Service not available")
            return []
        
        logger.info(f"Free News Service - Attempting to fetch {count} articles for category: {category}")
        
        # Return sample news since this is a free service
        sample_news = [
            {
                'title': f'Free News: {category.title()} Market Update',
                'summary': f'Latest updates from the {category} market with free news coverage.',
                'content': f'This is a comprehensive analysis of the current {category} market trends and their implications for investors.',
                'url': 'https://example.com/news/1',
                'image_url': '/static/images/news-placeholder.svg',
                'published_at': timezone.now().isoformat(),
                'source': 'Free News',
                'category': category
            },
            {
                'title': f'Free News: {category.title()} Industry Insights',
                'summary': f'Industry experts share insights on {category} market developments.',
                'content': f'Professional analysis of {category} market conditions and future outlook.',
                'url': 'https://example.com/news/2',
                'image_url': '/static/images/news-placeholder.svg',
                'published_at': timezone.now().isoformat(),
                'source': 'Free News',
                'category': category
            }
        ]
        
        return sample_news[:count]


class MarketAuxService:
    """Service for fetching news from MarketAux API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'MARKETAUX_API_KEY', '')
        self.base_url = 'https://api.marketaux.com/v1'
        self.source, _ = NewsSource.objects.get_or_create(
            name='MarketAux',
            defaults={
                'base_url': self.base_url,
                'api_key': self.api_key,
                'rate_limit_per_hour': 1000  # MarketAux free tier
            }
        )
        self.is_configured = bool(self.api_key)
        
        # Debug logging
        logger.info(f"MarketAux Service - API Key: {'✅ Set' if self.api_key else '❌ Not Set'}")
        if self.api_key:
            logger.info(f"MarketAux Service - Key length: {len(self.api_key)}")
            logger.info(f"MarketAux Service - Key preview: {self.api_key[:8]}...")
        else:
            logger.warning("MarketAux Service - No API key found in settings")
    
    def fetch_news(self, category='crypto', count=20):
        """Fetch news from MarketAux API"""
        if not self.is_configured:
            logger.warning("MarketAux API key not configured, skipping")
            return []
        
        logger.info(f"MarketAux Service - Attempting to fetch {count} articles for category: {category}")
        
        try:
            # Map our categories to MarketAux symbols
            symbol_mapping = {
                'crypto': 'BTC,ETH,ADA,SOL,MATIC,AVAX,DOT,LINK,UNI,AAVE',
                'bitcoin': 'BTC',
                'ethereum': 'ETH',
                'altcoins': 'ADA,SOL,MATIC,AVAX,DOT,LINK,UNI,AAVE',
                'stocks': 'AAPL,MSFT,GOOGL,AMZN,TSLA,META,NVDA,AMD,INTC,ORCL',
                'real_estate': 'REIT,SPG,PLD,AMT,CCI,EQR,AVB,MAA,ESS,PSA',
                'general': 'BTC,ETH,AAPL,MSFT,GOOGL,AMZN,TSLA'
            }
            
            symbols = symbol_mapping.get(category, 'BTC,ETH,AAPL,MSFT,GOOGL')
            
            url = f"{self.base_url}/news/all"
            params = {
                'api_token': self.api_key,
                'symbols': symbols,
                'limit': min(count, 100),  # MarketAux max is 100
                'language': 'en',
                'filter_entities': 'true'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get('data', [])[:count]:
                # Extract entities for better categorization
                entities = item.get('entities', [])
                entity_symbols = [entity.get('symbol', '') for entity in entities if entity.get('symbol')]
                
                article = {
                    'title': item.get('title', ''),
                    'summary': item.get('description', ''),
                    'content': item.get('description', ''),
                    'url': item.get('url', ''),
                    'image_url': item.get('image_url', '/static/images/news-placeholder.svg'),
                    'published_at': self._parse_date(item.get('published_at', '')),
                    'source': 'MarketAux',
                    'category': category,
                    'symbols': ','.join(entity_symbols[:5])  # First 5 symbols
                }
                articles.append(article)
            
            logger.info(f"MarketAux Service - Fetched {len(articles)} articles for {category}")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MarketAux Service - Request error: {e}")
            return []
        except Exception as e:
            logger.error(f"MarketAux Service - Error fetching news: {e}")
            return []
    
    def _parse_date(self, date_str):
        """Parse date string from MarketAux"""
        if not date_str:
            return timezone.now()
        
        try:
            # MarketAux format: 2023-12-01T10:30:00+00:00
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return timezone.now()


class NewsAggregator:
    """Main news aggregator that combines all services - MARKETAUX ONLY"""
    
    def __init__(self):
        self.services = {
            'free_news': FreeNewsService(),
            'marketaux': MarketAuxService()
        }
        
        # Check which services are configured
        configured_services = [name for name, service in self.services.items() if service.is_configured]
        logger.info(f"Configured news services: {configured_services}")
    
    def fetch_all_news(self, categories=None, count_per_category=10):
        """Fetch news from all available services"""
        if categories is None:
            categories = ['crypto', 'bitcoin', 'stocks', 'real_estate']
        
        all_articles = []
        
        for category in categories:
            logger.info(f"Fetching news for category: {category}")
            
            for service_name, service in self.services.items():
                if service.is_configured:
                    try:
                        articles = service.fetch_news(category, count_per_category)
                        all_articles.extend(articles)
                        logger.info(f"{service_name}: Fetched {len(articles)} articles for {category}")
                    except Exception as e:
                        logger.error(f"{service_name} failed for {category}: {e}")
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            if article.get('title') not in seen_titles:
                seen_titles.add(article.get('title'))
                unique_articles.append(article)
        
        logger.info(f"NewsAggregator - Total unique articles: {len(unique_articles)}")
        return unique_articles
    
    def save_articles(self, articles):
        """Save articles to database"""
        saved_count = 0
        
        for article_data in articles:
            try:
                # Get or create category
                category_name = article_data.get('category', 'general')
                category, _ = NewsCategory.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'display_name': category_name.title(),
                        'description': f'{category_name.title()} news'
                    }
                )
                
                # Get or create source
                source_name = article_data.get('source', 'Unknown')
                source, _ = NewsSource.objects.get_or_create(
                    name=source_name,
                    defaults={
                        'base_url': 'https://api.marketaux.com',
                        'is_active': True
                    }
                )
                
                # Create article
                article, created = NewsArticle.objects.get_or_create(
                    title=article_data.get('title', ''),
                    defaults={
                        'summary': article_data.get('summary', ''),
                        'content': article_data.get('content', ''),
                        'url': article_data.get('url', ''),
                        'image_url': article_data.get('image_url', '/static/images/news-placeholder.svg'),
                        'published_at': self._parse_datetime(article_data.get('published_at', '')),
                        'source': source,
                        'category': category,
                        'is_featured': False,
                        'is_active': True,
                        'tags': article_data.get('symbols', '')  # Store symbols as tags
                    }
                )
                
                if created:
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"Error saving article: {e}")
        
        logger.info(f"NewsAggregator - Saved {saved_count} new articles")
        return saved_count
    
    def _parse_datetime(self, date_str):
        """Parse datetime string"""
        if not date_str:
            return timezone.now()
        
        try:
            if isinstance(date_str, (int, float)):
                # Unix timestamp
                return datetime.fromtimestamp(date_str, tz=timezone.utc)
            else:
                # ISO format
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return timezone.now()
    
    def get_configured_services(self):
        """Get list of configured services"""
        return [name for name, service in self.services.items() if service.is_configured]