"""
News services for fetching and processing news from various APIs
"""
import requests
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from .news_models import NewsSource, NewsCategory, NewsArticle, NewsCache
import hashlib
import time

logger = logging.getLogger(__name__)


class BaseNewsService:
    """Base class for news services"""
    
    def __init__(self, source_name):
        self.source = NewsSource.objects.get(name=source_name)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MeridianAssetLogistics/1.0'
        })
    
    def get_cache_key(self, endpoint, params=None):
        """Generate cache key for API request"""
        key_data = f"{self.source.name}:{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def make_request(self, url, params=None, cache_minutes=15):
        """Make API request with caching"""
        cache_key = self.get_cache_key(url, params)
        
        # Check cache first
        cached_data = NewsCache.get_data(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {self.source.name}: {url}")
            return cached_data
        
        try:
            # Rate limiting check
            if not self._check_rate_limit():
                logger.warning(f"Rate limit exceeded for {self.source.name}")
                return None
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            NewsCache.set_data(cache_key, data, cache_minutes)
            
            # Update last fetch time
            self.source.last_fetch = timezone.now()
            self.source.save(update_fields=['last_fetch'])
            
            logger.info(f"Successfully fetched data from {self.source.name}: {url}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from {self.source.name}: {e}")
            return None
    
    def _check_rate_limit(self):
        """Check if we're within rate limits"""
        if not self.source.last_fetch:
            return True
        
        time_since_last = timezone.now() - self.source.last_fetch
        min_interval = timedelta(hours=1) / self.source.rate_limit_per_hour
        
        return time_since_last >= min_interval


class CoinGeckoService(BaseNewsService):
    """Service for CoinGecko API"""
    
    def __init__(self):
        super().__init__('CoinGecko')
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = getattr(settings, 'COINGECKO_API_KEY', '')
    
    def get_crypto_news(self, limit=50):
        """Get cryptocurrency news"""
        url = f"{self.base_url}/news"
        params = {
            'per_page': limit,
            'page': 1
        }
        
        # Add API key if available
        if self.api_key:
            params['x_cg_demo_api_key'] = self.api_key
        
        data = self.make_request(url, params)
        if not data:
            return []
        
        return self._process_coingecko_articles(data.get('data', []))
    
    def get_bitcoin_news(self, limit=20):
        """Get Bitcoin-specific news"""
        return self.get_crypto_news(limit)
    
    def get_ethereum_news(self, limit=20):
        """Get Ethereum-specific news"""
        return self.get_crypto_news(limit)
    
    def _process_coingecko_articles(self, articles):
        """Process CoinGecko articles into our format"""
        processed = []
        crypto_category = NewsCategory.objects.get_or_create(
            name='crypto',
            defaults={'display_name': 'Cryptocurrency', 'description': 'Cryptocurrency news'}
        )[0]
        
        for article in articles:
            try:
                processed_article = {
                    'title': article.get('title', ''),
                    'summary': article.get('description', ''),
                    'url': article.get('url', ''),
                    'image_url': article.get('thumb_2x', ''),
                    'published_at': self._parse_timestamp(article.get('updated_at')),
                    'author': article.get('source', ''),
                    'tags': [tag.get('name', '') for tag in article.get('tags', [])],
                    'category': crypto_category,
                    'source': self.source
                }
                processed.append(processed_article)
            except Exception as e:
                logger.error(f"Error processing CoinGecko article: {e}")
                continue
        
        return processed
    
    def _parse_timestamp(self, timestamp):
        """Parse Unix timestamp"""
        if not timestamp:
            return timezone.now()
        
        try:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (ValueError, TypeError):
            return timezone.now()


class CryptoPanicService(BaseNewsService):
    """Service for CryptoPanic API"""
    
    def __init__(self):
        super().__init__('CryptoPanic')
        self.base_url = "https://cryptopanic.com/api/developer/v2"
        self.api_key = getattr(settings, 'CRYPTOPANIC_API_KEY', '')
    
    def get_crypto_news(self, limit=50):
        """Get cryptocurrency news"""
        url = f"{self.base_url}/posts"
        params = {
            'auth_token': self.api_key,
            'public': 'true',
            'currencies': 'BTC,ETH',
            'page_size': limit
        }
        
        data = self.make_request(url, params)
        if not data:
            return []
        
        return self._process_cryptopanic_articles(data.get('results', []))
    
    def get_bitcoin_news(self, limit=20):
        """Get Bitcoin-specific news"""
        url = f"{self.base_url}/posts"
        params = {
            'auth_token': self.api_key,
            'public': 'true',
            'currencies': 'BTC',
            'page_size': limit
        }
        
        data = self.make_request(url, params)
        if not data:
            return []
        
        return self._process_cryptopanic_articles(data.get('results', []))
    
    def get_ethereum_news(self, limit=20):
        """Get Ethereum-specific news"""
        url = f"{self.base_url}/posts"
        params = {
            'auth_token': self.api_key,
            'public': 'true',
            'currencies': 'ETH',
            'page_size': limit
        }
        
        data = self.make_request(url, params)
        if not data:
            return []
        
        return self._process_cryptopanic_articles(data.get('results', []))
    
    def _process_cryptopanic_articles(self, articles):
        """Process CryptoPanic articles into our format"""
        processed = []
        crypto_category = NewsCategory.objects.get_or_create(
            name='crypto',
            defaults={'display_name': 'Cryptocurrency', 'description': 'Cryptocurrency news'}
        )[0]
        
        for article in articles:
            try:
                processed_article = {
                    'title': article.get('title', ''),
                    'summary': article.get('title', ''),  # CryptoPanic doesn't have separate summary
                    'url': article.get('url', ''),
                    'image_url': '',
                    'published_at': self._parse_date(article.get('published_at')),
                    'author': article.get('source', {}).get('title', ''),
                    'tags': [currency.get('code', '') for currency in article.get('currencies', [])],
                    'category': crypto_category,
                    'source': self.source
                }
                processed.append(processed_article)
            except Exception as e:
                logger.error(f"Error processing CryptoPanic article: {e}")
                continue
        
        return processed


class CoinDeskService(BaseNewsService):
    """Service for CoinDesk API"""
    
    def __init__(self):
        super().__init__('CoinDesk')
        self.base_url = "https://api.coindesk.com/v1"
        self.api_key = getattr(settings, 'COINDESK_API_KEY', '')
    
    def get_crypto_news(self, limit=50):
        """Get cryptocurrency news"""
        url = f"{self.base_url}/news"
        params = {
            'limit': limit
        }
        
        # Add API key if available
        if self.api_key:
            params['api_key'] = self.api_key
        
        data = self.make_request(url, params)
        if not data:
            return []
        
        return self._process_coindesk_articles(data.get('data', []))
    
    def get_bitcoin_news(self, limit=20):
        """Get Bitcoin-specific news"""
        return self.get_crypto_news(limit)
    
    def get_ethereum_news(self, limit=20):
        """Get Ethereum-specific news"""
        return self.get_crypto_news(limit)
    
    def _process_coindesk_articles(self, articles):
        """Process CoinDesk articles into our format"""
        processed = []
        crypto_category = NewsCategory.objects.get_or_create(
            name='crypto',
            defaults={'display_name': 'Cryptocurrency', 'description': 'Cryptocurrency news'}
        )[0]
        
        for article in articles:
            try:
                processed_article = {
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'image_url': article.get('image', ''),
                    'published_at': self._parse_date(article.get('published_at')),
                    'author': article.get('author', ''),
                    'tags': article.get('tags', []),
                    'category': crypto_category,
                    'source': self.source
                }
                processed.append(processed_article)
            except Exception as e:
                logger.error(f"Error processing CoinDesk article: {e}")
                continue
        
        return processed


class NewsAPIService(BaseNewsService):
    """Service for NewsAPI"""
    
    def __init__(self):
        super().__init__('NewsAPI')
        self.base_url = "https://newsapi.org/v2"
        self.api_key = getattr(settings, 'NEWSAPI_KEY', '')
    
    def get_finance_news(self, limit=50):
        """Get general finance news"""
        url = f"{self.base_url}/everything"
        params = {
            'q': 'finance OR investment OR stock market OR real estate',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': limit,
            'apiKey': self.api_key
        }
        
        data = self.make_request(url, params)
        if not data:
            return []
        
        return self._process_newsapi_articles(data.get('articles', []))
    
    def get_stock_news(self, limit=30):
        """Get stock market news"""
        url = f"{self.base_url}/everything"
        params = {
            'q': 'stock market OR stocks OR trading OR NASDAQ OR NYSE',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': limit,
            'apiKey': self.api_key
        }
        
        data = self.make_request(url, params)
        if not data:
            return []
        
        return self._process_newsapi_articles(data.get('articles', []), 'stocks')
    
    def get_real_estate_news(self, limit=20):
        """Get real estate news"""
        url = f"{self.base_url}/everything"
        params = {
            'q': 'real estate OR property OR housing OR mortgage',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': limit,
            'apiKey': self.api_key
        }
        
        data = self.make_request(url, params)
        if not data:
            return []
        
        return self._process_newsapi_articles(data.get('articles', []), 'real_estate')
    
    def _process_newsapi_articles(self, articles, category_name='general'):
        """Process NewsAPI articles into our format"""
        processed = []
        category = NewsCategory.objects.get_or_create(
            name=category_name,
            defaults={'display_name': category_name.title(), 'description': f'{category_name.title()} news'}
        )[0]
        
        for article in articles:
            try:
                processed_article = {
                    'title': article.get('title', ''),
                    'summary': article.get('description', ''),
                    'url': article.get('url', ''),
                    'image_url': article.get('urlToImage', ''),
                    'published_at': self._parse_date(article.get('publishedAt')),
                    'author': article.get('author', ''),
                    'tags': [],
                    'category': category,
                    'source': self.source
                }
                processed.append(processed_article)
            except Exception as e:
                logger.error(f"Error processing NewsAPI article: {e}")
                continue
        
        return processed


class FinnhubService(BaseNewsService):
    """Service for Finnhub API"""
    
    def __init__(self):
        super().__init__('Finnhub')
        self.base_url = "https://finnhub.io/api/v1"
        self.api_key = getattr(settings, 'FINNHUB_API_KEY', '')
    
    def get_company_news(self, symbol='AAPL', limit=50):
        """Get company-specific news"""
        url = f"{self.base_url}/company-news"
        params = {
            'symbol': symbol,
            'from': (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'to': timezone.now().strftime('%Y-%m-%d'),
            'token': self.api_key
        }
        
        data = self.make_request(url, params)
        if not data:
            return []
        
        return self._process_finnhub_articles(data[:limit])
    
    def get_general_news(self, category='general', limit=50):
        """Get general market news"""
        url = f"{self.base_url}/news"
        params = {
            'category': category,
            'token': self.api_key
        }
        
        data = self.make_request(url, params)
        if not data:
            return []
        
        return self._process_finnhub_articles(data[:limit])
    
    def _process_finnhub_articles(self, articles):
        """Process Finnhub articles into our format"""
        processed = []
        stocks_category = NewsCategory.objects.get_or_create(
            name='stocks',
            defaults={'display_name': 'Stock Market', 'description': 'Stock market news'}
        )[0]
        
        for article in articles:
            try:
                processed_article = {
                    'title': article.get('headline', ''),
                    'summary': article.get('summary', ''),
                    'url': article.get('url', ''),
                    'image_url': '',
                    'published_at': self._parse_timestamp(article.get('datetime')),
                    'author': '',
                    'tags': article.get('related', '').split(',') if article.get('related') else [],
                    'category': stocks_category,
                    'source': self.source
                }
                processed.append(processed_article)
            except Exception as e:
                logger.error(f"Error processing Finnhub article: {e}")
                continue
        
        return processed


class NewsAggregatorService:
    """Main service to aggregate news from all sources"""
    
    def __init__(self):
        self.services = {
            'crypto_coindesk': CoinDeskService(),
            'crypto_cryptopanic': CryptoPanicService(),
            'general': NewsAPIService(),
            'stocks': FinnhubService(),
        }
    
    def fetch_all_news(self, limit_per_category=20):
        """Fetch news from all sources"""
        all_articles = []
        
        try:
            # Fetch crypto news from CoinDesk (you have this API key)
            try:
                crypto_articles = self.services['crypto_coindesk'].get_crypto_news(limit_per_category)
                all_articles.extend(crypto_articles)
                logger.info(f"Fetched {len(crypto_articles)} articles from CoinDesk")
            except Exception as e:
                logger.warning(f"CoinDesk service failed: {e}")
            
            # Fetch crypto news from CryptoPanic (if you get the API key)
            try:
                crypto_articles = self.services['crypto_cryptopanic'].get_crypto_news(limit_per_category)
                all_articles.extend(crypto_articles)
                logger.info(f"Fetched {len(crypto_articles)} articles from CryptoPanic")
            except Exception as e:
                logger.warning(f"CryptoPanic service failed: {e}")
            
            # Fetch Bitcoin news from CoinDesk
            try:
                btc_articles = self.services['crypto_coindesk'].get_bitcoin_news(10)
                all_articles.extend(btc_articles)
            except Exception as e:
                logger.warning(f"Bitcoin news from CoinDesk failed: {e}")
            
            # Fetch Ethereum news from CoinDesk
            try:
                eth_articles = self.services['crypto_coindesk'].get_ethereum_news(10)
                all_articles.extend(eth_articles)
            except Exception as e:
                logger.warning(f"Ethereum news from CoinDesk failed: {e}")
            
            # Fetch stock news from NewsAPI (you have this API key)
            try:
                stock_articles = self.services['general'].get_stock_news(limit_per_category)
                all_articles.extend(stock_articles)
                logger.info(f"Fetched {len(stock_articles)} stock articles from NewsAPI")
            except Exception as e:
                logger.warning(f"Stock news from NewsAPI failed: {e}")
            
            # Fetch real estate news from NewsAPI
            try:
                real_estate_articles = self.services['general'].get_real_estate_news(15)
                all_articles.extend(real_estate_articles)
                logger.info(f"Fetched {len(real_estate_articles)} real estate articles from NewsAPI")
            except Exception as e:
                logger.warning(f"Real estate news from NewsAPI failed: {e}")
            
            # Fetch general finance news from NewsAPI
            try:
                finance_articles = self.services['general'].get_finance_news(limit_per_category)
                all_articles.extend(finance_articles)
                logger.info(f"Fetched {len(finance_articles)} finance articles from NewsAPI")
            except Exception as e:
                logger.warning(f"Finance news from NewsAPI failed: {e}")
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
        
        return all_articles
    
    def save_articles(self, articles):
        """Save articles to database"""
        saved_count = 0
        
        for article_data in articles:
            try:
                # Check if article already exists
                if NewsArticle.objects.filter(url=article_data['url']).exists():
                    continue
                
                # Create new article
                article = NewsArticle.objects.create(**article_data)
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving article: {e}")
                continue
        
        logger.info(f"Saved {saved_count} new articles")
        return saved_count
    
    def get_latest_news(self, category=None, limit=50, featured_only=False):
        """Get latest news from database"""
        queryset = NewsArticle.objects.filter(is_active=True)
        
        if category:
            queryset = queryset.filter(category__name=category)
        
        if featured_only:
            queryset = queryset.filter(is_featured=True)
        
        return queryset.order_by('-published_at')[:limit]
    
    def update_featured_news(self, count=5):
        """Update featured news based on relevance and recency"""
        # Reset all featured flags
        NewsArticle.objects.update(is_featured=False)
        
        # Get most relevant recent articles
        recent_articles = NewsArticle.objects.filter(
            is_active=True,
            published_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-relevance_score', '-view_count', '-published_at')[:count]
        
        # Mark as featured
        for article in recent_articles:
            article.is_featured = True
            article.save(update_fields=['is_featured'])
    
    def _parse_date(self, date_string):
        """Parse various date formats"""
        if not date_string:
            return timezone.now()
        
        formats = [
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        
        return timezone.now()
    
    def _parse_timestamp(self, timestamp):
        """Parse Unix timestamp"""
        if not timestamp:
            return timezone.now()
        
        try:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (ValueError, TypeError):
            return timezone.now()
