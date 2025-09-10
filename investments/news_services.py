"""
News API services for fetching real news from various sources
"""
import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .news_models import NewsArticle, NewsCategory, NewsSource
import json

logger = logging.getLogger(__name__)


class NewsAPIService:
    """Service for fetching news from NewsAPI"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'NEWSAPI_KEY', '')
        self.base_url = 'https://newsapi.org/v2'
        self.source, _ = NewsSource.objects.get_or_create(
            name='NewsAPI',
            defaults={
                'base_url': self.base_url,
                'api_key': self.api_key,
                'rate_limit_per_hour': 1000
            }
        )
        self.is_configured = bool(self.api_key)
        
        # Debug logging
        logger.info(f"NewsAPI Service - API Key: {'✅ Set' if self.api_key else '❌ Not Set'}")
        if self.api_key:
            logger.info(f"NewsAPI Service - Key length: {len(self.api_key)}")
            logger.info(f"NewsAPI Service - Key preview: {self.api_key[:8]}...")
    
    def fetch_news(self, category='business', count=20):
        """Fetch news from NewsAPI"""
        if not self.is_configured:
            logger.warning("NewsAPI key not configured, skipping")
            return []
        
        logger.info(f"NewsAPI Service - Attempting to fetch {count} articles for category: {category}")
        
        try:
            # Map our categories to NewsAPI categories
            category_mapping = {
                'crypto': 'business',
                'stocks': 'business', 
                'real_estate': 'business',
                'bitcoin': 'business',
                'ethereum': 'business',
                'altcoins': 'business',
                'general': 'general'
            }
            
            api_category = category_mapping.get(category, 'business')
            
            url = f"{self.base_url}/everything"
            params = {
                'apiKey': self.api_key,
                'q': self._get_search_query(category),
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': min(count, 100),  # NewsAPI max is 100
                'from': (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            logger.info(f"NewsAPI: Fetched {len(articles)} articles for {category}")
            return self._process_articles(articles, category)
            
        except Exception as e:
            logger.error(f"Error fetching NewsAPI data: {e}")
            return []
    
    def _get_search_query(self, category):
        """Get search query based on category"""
        queries = {
            'crypto': 'cryptocurrency OR bitcoin OR ethereum OR blockchain',
            'bitcoin': 'bitcoin OR BTC',
            'ethereum': 'ethereum OR ETH',
            'altcoins': 'altcoin OR cryptocurrency OR crypto',
            'stocks': 'stock market OR stocks OR trading OR S&P 500',
            'real_estate': 'real estate OR property OR housing',
            'general': 'finance OR economy OR business'
        }
        return queries.get(category, 'finance')
    
    def _process_articles(self, articles, category):
        """Process articles and create NewsArticle objects"""
        processed = []
        category_obj, _ = NewsCategory.objects.get_or_create(
            name=category,
            defaults={
                'display_name': category.replace('_', ' ').title(),
                'description': f'News about {category.replace("_", " ")}'
            }
        )
        
        for article in articles:
            try:
                # Check if article already exists
                if NewsArticle.objects.filter(url=article.get('url')).exists():
                    continue
                
                news_article = NewsArticle.objects.create(
                    title=article.get('title', '')[:200],
                    summary=article.get('description', '')[:500],
                    content=article.get('content', '')[:2000] if article.get('content') else '',
                    url=article.get('url', ''),
                    image_url=article.get('urlToImage', ''),
                    source=self.source,
                    category=category_obj,
                    published_at=self._parse_date(article.get('publishedAt')),
                    author=article.get('author', '')[:100] if article.get('author') else '',
                    is_active=True
                )
                processed.append(news_article)
                
            except Exception as e:
                logger.error(f"Error processing NewsAPI article: {e}")
                continue
        
        return processed
    
    def _parse_date(self, date_str):
        """Parse date string to datetime"""
        if not date_str:
            return timezone.now()
        
        try:
            # NewsAPI format: 2023-12-01T10:30:00Z
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return timezone.now()


class FinnhubService:
    """Service for fetching news from Finnhub"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'FINNHUB_API_KEY', '')
        self.base_url = 'https://finnhub.io/api/v1'
        self.source, _ = NewsSource.objects.get_or_create(
            name='Finnhub',
            defaults={
                'base_url': self.base_url,
                'api_key': self.api_key,
                'rate_limit_per_hour': 60  # Finnhub free tier limit
            }
        )
        self.is_configured = bool(self.api_key)
        
        # Debug logging
        logger.info(f"Finnhub Service - API Key: {'✅ Set' if self.api_key else '❌ Not Set'}")
        if self.api_key:
            logger.info(f"Finnhub Service - Key length: {len(self.api_key)}")
            logger.info(f"Finnhub Service - Key preview: {self.api_key[:8]}...")
    
    def fetch_news(self, category='stocks', count=20):
        """Fetch news from Finnhub"""
        if not self.is_configured:
            logger.info("Finnhub API key not configured, skipping")
            return []
        
        try:
            # Finnhub categories
            category_mapping = {
                'stocks': 'general',
                'crypto': 'crypto',
                'bitcoin': 'crypto',
                'ethereum': 'crypto',
                'altcoins': 'crypto',
                'real_estate': 'general'
            }
            
            api_category = category_mapping.get(category, 'general')
            
            url = f"{self.base_url}/news"
            params = {
                'token': self.api_key,
                'category': api_category
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            articles = response.json()
            
            logger.info(f"Finnhub: Fetched {len(articles)} articles for {category}")
            return self._process_articles(articles[:count], category)
            
        except Exception as e:
            logger.error(f"Error fetching Finnhub data: {e}")
            return []
    
    def _process_articles(self, articles, category):
        """Process articles and create NewsArticle objects"""
        processed = []
        category_obj, _ = NewsCategory.objects.get_or_create(
            name=category,
            defaults={
                'display_name': category.replace('_', ' ').title(),
                'description': f'News about {category.replace("_", " ")}'
            }
        )
        
        for article in articles:
            try:
                # Check if article already exists
                if NewsArticle.objects.filter(url=article.get('url')).exists():
                    continue
                
                news_article = NewsArticle.objects.create(
                    title=article.get('headline', '')[:200],
                    summary=article.get('summary', '')[:500],
                    content=article.get('summary', '')[:2000],
                    url=article.get('url', ''),
                    image_url=article.get('image', ''),
                    source=self.source,
                    category=category_obj,
                    published_at=self._parse_timestamp(article.get('datetime')),
                    author=article.get('source', '')[:100] if article.get('source') else '',
                    is_active=True
                )
                processed.append(news_article)
                
            except Exception as e:
                logger.error(f"Error processing Finnhub article: {e}")
                continue
        
        return processed
    
    def _parse_timestamp(self, timestamp):
        """Parse Unix timestamp to datetime"""
        if not timestamp:
            return timezone.now()
        
        try:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except:
            return timezone.now()


class CryptoPanicService:
    """Service for fetching news from CryptoPanic"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'CRYPTOPANIC_API_KEY', '')
        self.base_url = 'https://cryptopanic.com/api/v1'
        self.source, _ = NewsSource.objects.get_or_create(
            name='CryptoPanic',
            defaults={
                'base_url': self.base_url,
                'api_key': self.api_key,
                'rate_limit_per_hour': 100
            }
        )
        self.is_configured = bool(self.api_key)
    
    def fetch_news(self, category='crypto', count=20):
        """Fetch news from CryptoPanic"""
        if not self.is_configured:
            logger.info("CryptoPanic API key not configured, skipping")
            return []
        
        try:
            url = f"{self.base_url}/posts"
            params = {
                'auth_token': self.api_key,
                'public': 'true',
                'currencies': self._get_currencies(category),
                'page_size': min(count, 20)  # CryptoPanic max is 20
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('results', [])
            
            logger.info(f"CryptoPanic: Fetched {len(articles)} articles for {category}")
            return self._process_articles(articles, category)
            
        except Exception as e:
            logger.error(f"Error fetching CryptoPanic data: {e}")
            return []
    
    def _get_currencies(self, category):
        """Get currencies based on category"""
        currency_mapping = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'crypto': 'BTC,ETH',
            'altcoins': 'BTC,ETH,ADA,DOT,LINK'
        }
        return currency_mapping.get(category, 'BTC,ETH')
    
    def _process_articles(self, articles, category):
        """Process articles and create NewsArticle objects"""
        processed = []
        category_obj, _ = NewsCategory.objects.get_or_create(
            name=category,
            defaults={
                'display_name': category.replace('_', ' ').title(),
                'description': f'News about {category.replace("_", " ")}'
            }
        )
        
        for article in articles:
            try:
                # Check if article already exists
                if NewsArticle.objects.filter(url=article.get('url')).exists():
                    continue
                
                news_article = NewsArticle.objects.create(
                    title=article.get('title', '')[:200],
                    summary=article.get('meta', {}).get('description', '')[:500],
                    content=article.get('meta', {}).get('description', '')[:2000],
                    url=article.get('url', ''),
                    image_url=article.get('meta', {}).get('image', ''),
                    source=self.source,
                    category=category_obj,
                    published_at=self._parse_date(article.get('published_at')),
                    author=article.get('source', {}).get('title', '')[:100] if article.get('source') else '',
                    is_active=True
                )
                processed.append(news_article)
                
            except Exception as e:
                logger.error(f"Error processing CryptoPanic article: {e}")
                continue
        
        return processed
    
    def _parse_date(self, date_str):
        """Parse date string to datetime"""
        if not date_str:
            return timezone.now()
        
        try:
            # CryptoPanic format: 2023-12-01T10:30:00Z
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return timezone.now()


class CoinDeskService:
    """Service for fetching news from CoinDesk"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'COINDESK_API_KEY', '')
        self.base_url = 'https://api.coindesk.com/v1'
        self.source, _ = NewsSource.objects.get_or_create(
            name='CoinDesk',
            defaults={
                'base_url': self.base_url,
                'api_key': self.api_key,
                'rate_limit_per_hour': 1000
            }
        )
        self.is_configured = bool(self.api_key)
    
    def fetch_news(self, category='bitcoin', count=20):
        """Fetch news from CoinDesk"""
        try:
            # CoinDesk doesn't require API key for basic news
            url = f"{self.base_url}/news"
            params = {
                'limit': min(count, 50)
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('data', [])
            
            logger.info(f"CoinDesk: Fetched {len(articles)} articles for {category}")
            return self._process_articles(articles, category)
            
        except Exception as e:
            logger.error(f"Error fetching CoinDesk data: {e}")
            return []
    
    def _process_articles(self, articles, category):
        """Process articles and create NewsArticle objects"""
        processed = []
        category_obj, _ = NewsCategory.objects.get_or_create(
            name=category,
            defaults={
                'display_name': category.replace('_', ' ').title(),
                'description': f'News about {category.replace("_", " ")}'
            }
        )
        
        for article in articles:
            try:
                # Check if article already exists
                if NewsArticle.objects.filter(url=article.get('url')).exists():
                    continue
                
                news_article = NewsArticle.objects.create(
                    title=article.get('title', '')[:200],
                    summary=article.get('excerpt', '')[:500],
                    content=article.get('content', '')[:2000] if article.get('content') else '',
                    url=article.get('url', ''),
                    image_url=article.get('featured_image', ''),
                    source=self.source,
                    category=category_obj,
                    published_at=self._parse_date(article.get('published_at')),
                    author=article.get('author', {}).get('name', '')[:100] if article.get('author') else '',
                    is_active=True
                )
                processed.append(news_article)
                
            except Exception as e:
                logger.error(f"Error processing CoinDesk article: {e}")
                continue
        
        return processed
    
    def _parse_date(self, date_str):
        """Parse date string to datetime"""
        if not date_str:
            return timezone.now()
        
        try:
            # CoinDesk format: 2023-12-01T10:30:00Z
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return timezone.now()


class NewsAggregator:
    """Main news aggregator that combines all services"""
    
    def __init__(self):
        self.services = {
            'newsapi': NewsAPIService(),
            'finnhub': FinnhubService(),
            'cryptopanic': CryptoPanicService(),
            'coindesk': CoinDeskService()
        }
        
        # Check which services are configured
        configured_services = [name for name, service in self.services.items() if service.is_configured]
        logger.info(f"Configured news services: {configured_services}")
    
    def fetch_all_news(self, categories=None, count_per_category=10):
        """Fetch news from all available services"""
        if categories is None:
            categories = ['crypto', 'bitcoin', 'stocks', 'real_estate']
        
        all_articles = []
        total_fetched = 0
        
        for category in categories:
            logger.info(f"Fetching news for category: {category}")
            category_articles = []
            
            # Try different services based on category
            if category in ['crypto', 'bitcoin', 'ethereum', 'altcoins']:
                # Use crypto-focused services
                services_to_try = ['cryptopanic', 'coindesk', 'newsapi']
            else:
                # Use general financial services
                services_to_try = ['newsapi', 'finnhub']
            
            for service_name in services_to_try:
                try:
                    service = self.services[service_name]
                    if not service.is_configured:
                        logger.info(f"Skipping {service_name} - not configured")
                        continue
                        
                    articles = service.fetch_news(category, count_per_category)
                    category_articles.extend(articles)
                    total_fetched += len(articles)
                    
                    logger.info(f"Fetched {len(articles)} articles from {service_name} for {category}")
                    
                    # Don't try other services if we got enough articles
                    if len(category_articles) >= count_per_category:
                        break
                        
                except Exception as e:
                    logger.error(f"Error with {service_name} for {category}: {e}")
                    continue
            
            all_articles.extend(category_articles)
        
        # Mark some articles as featured
        if all_articles:
            self._mark_featured_articles(all_articles)
        
        logger.info(f"Total articles fetched: {total_fetched}")
        return all_articles
    
    def _mark_featured_articles(self, articles):
        """Mark some articles as featured based on certain criteria"""
        if not articles:
            return
        
        # Sort by published date (newest first)
        articles.sort(key=lambda x: x.published_at, reverse=True)
        
        # Mark top 20% as featured
        featured_count = max(1, len(articles) // 5)
        
        for i, article in enumerate(articles[:featured_count]):
            if i < featured_count:
                article.is_featured = True
                article.save()
    
    def get_news_stats(self):
        """Get statistics about news articles"""
        total_articles = NewsArticle.objects.count()
        featured_articles = NewsArticle.objects.filter(is_featured=True).count()
        active_articles = NewsArticle.objects.filter(is_active=True).count()
        
        by_category = {}
        for category in NewsCategory.objects.all():
            count = NewsArticle.objects.filter(category=category).count()
            by_category[category.name] = count
        
        by_source = {}
        for source in NewsSource.objects.all():
            count = NewsArticle.objects.filter(source=source).count()
            by_source[source.name] = count
        
        return {
            'total_articles': total_articles,
            'featured_articles': featured_articles,
            'active_articles': active_articles,
            'by_category': by_category,
            'by_source': by_source
        }
    
    def get_configured_services(self):
        """Get list of configured services"""
        return [name for name, service in self.services.items() if service.is_configured]