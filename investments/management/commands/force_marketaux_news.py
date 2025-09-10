"""
Management command to force fetch MarketAux news after server startup
"""
from django.core.management.base import BaseCommand
import requests
import os
from datetime import datetime
from django.utils import timezone

class Command(BaseCommand):
    help = 'Force fetch MarketAux news after server startup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of articles to fetch'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write("🚀 FORCE MARKETAUX NEWS FETCH")
        self.stdout.write("=" * 60)
        
        # Get API keys directly from environment
        marketaux_key = os.environ.get('MARKETAUX_API_KEY')
        cryptonews_key = os.environ.get('CRYPTONEWS_API_KEY')
        
        self.stdout.write(f"MARKETAUX_API_KEY: {'✅ Set' if marketaux_key else '❌ Not Set'}")
        self.stdout.write(f"CRYPTONEWS_API_KEY: {'✅ Set' if cryptonews_key else '❌ Not Set'}")
        
        if not marketaux_key and not cryptonews_key:
            self.stdout.write("❌ No API keys found!")
            return
        
        if marketaux_key:
            self.stdout.write(f"MarketAux key length: {len(marketaux_key)}")
            self.stdout.write(f"MarketAux key preview: {marketaux_key[:8]}...")
        
        if cryptonews_key:
            self.stdout.write(f"CryptoNews key length: {len(cryptonews_key)}")
            self.stdout.write(f"CryptoNews key preview: {cryptonews_key[:8]}...")
        
        # Test MarketAux API call
        if marketaux_key:
            self.stdout.write(f"\n🌐 TESTING MARKETAUX API...")
            try:
                url = "https://api.marketaux.com/v1/news/all"
                params = {
                    'api_token': marketaux_key,
                    'symbols': 'BTC,ETH,AAPL,MSFT,GOOGL,TSLA,AMZN,META,NVDA,AMD',
                    'limit': count,
                    'language': 'en',
                    'filter_entities': 'true'
                }
                
                response = requests.get(url, params=params, timeout=30)
                self.stdout.write(f"MarketAux Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('data', [])
                    self.stdout.write(f"✅ MarketAux Success: {len(articles)} articles returned")
                    
                    if articles:
                        # Save to database
                        self.save_articles(articles)
                    else:
                        self.stdout.write("No articles in MarketAux response")
                else:
                    self.stdout.write(f"❌ MarketAux Error: {response.status_code}")
                    self.stdout.write(f"Error: {response.text[:200]}...")
                    
            except Exception as e:
                self.stdout.write(f"❌ MarketAux Exception: {e}")
        
        # Test CryptoNewsAPI call
        if cryptonews_key:
            self.stdout.write(f"\n🌐 TESTING CRYPTONEWS API...")
            try:
                url = "https://cryptonewsapi.online/api/v1"
                params = {
                    'tickers': 'BTC,ETH,ADA,SOL,MATIC,AVAX',
                    'items': min(count, 50),
                    'token': cryptonews_key
                }
                
                response = requests.get(url, params=params, timeout=30)
                self.stdout.write(f"CryptoNews Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('data', [])
                    self.stdout.write(f"✅ CryptoNews Success: {len(articles)} articles returned")
                    
                    if articles:
                        # Save crypto articles to database
                        self.save_crypto_articles(articles)
                    else:
                        self.stdout.write("No articles in CryptoNews response")
                else:
                    self.stdout.write(f"❌ CryptoNews Error: {response.status_code}")
                    self.stdout.write(f"Error: {response.text[:200]}...")
                    
            except Exception as e:
                self.stdout.write(f"❌ CryptoNews Exception: {e}")

    def save_articles(self, articles):
        """Save articles to database"""
        try:
            from investments.news_models import NewsArticle, NewsCategory, NewsSource
            
            # Clear existing articles
            NewsArticle.objects.all().delete()
            self.stdout.write("🗑️  Cleared existing articles")
            
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
                        self.stdout.write(f"  {i+1}. {article.title[:50]}...")
                    
                except Exception as e:
                    self.stdout.write(f"Error saving article {i+1}: {e}")
                    continue
            
            self.stdout.write(f"✅ Saved {saved_count} articles to database")
            
            # Show final stats
            total_articles = NewsArticle.objects.count()
            featured_articles = NewsArticle.objects.filter(is_featured=True).count()
            active_articles = NewsArticle.objects.filter(is_active=True).count()
            
            self.stdout.write(f"📊 FINAL STATS: {total_articles} total, {featured_articles} featured, {active_articles} active")
            
        except Exception as e:
            self.stdout.write(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()

    def save_crypto_articles(self, articles):
        """Save crypto articles to database"""
        try:
            from investments.news_models import NewsArticle, NewsCategory, NewsSource
            from django.utils import timezone
            from datetime import datetime
            
            # Create crypto categories
            crypto_cat = NewsCategory.objects.get_or_create(
                name='crypto',
                defaults={'display_name': 'Cryptocurrency', 'description': 'Crypto news'}
            )[0]
            
            bitcoin_cat = NewsCategory.objects.get_or_create(
                name='bitcoin',
                defaults={'display_name': 'Bitcoin', 'description': 'Bitcoin news'}
            )[0]
            
            ethereum_cat = NewsCategory.objects.get_or_create(
                name='ethereum',
                defaults={'display_name': 'Ethereum', 'description': 'Ethereum news'}
            )[0]
            
            altcoins_cat = NewsCategory.objects.get_or_create(
                name='altcoins',
                defaults={'display_name': 'Altcoins', 'description': 'Altcoin news'}
            )[0]
            
            # Create source
            source, _ = NewsSource.objects.get_or_create(
                name='CryptoNewsAPI',
                defaults={
                    'base_url': 'https://cryptonewsapi.online',
                    'is_active': True
                }
            )
            
            # Save articles
            saved_count = 0
            for i, article_data in enumerate(articles):
                try:
                    # Determine category based on tickers
                    tickers = article_data.get('tickers', [])
                    category_name = 'crypto'  # Default
                    
                    if 'BTC' in tickers:
                        category_name = 'bitcoin'
                    elif 'ETH' in tickers:
                        category_name = 'ethereum'
                    elif any(ticker in ['ADA', 'SOL', 'MATIC', 'AVAX', 'DOT', 'LINK', 'UNI', 'AAVE'] for ticker in tickers):
                        category_name = 'altcoins'
                    
                    # Map category name to category object
                    category_map = {
                        'crypto': crypto_cat,
                        'bitcoin': bitcoin_cat,
                        'ethereum': ethereum_cat,
                        'altcoins': altcoins_cat
                    }
                    category = category_map.get(category_name, crypto_cat)
                    
                    # Parse published date
                    published_at = timezone.now()
                    if article_data.get('date'):
                        try:
                            published_at = datetime.fromisoformat(
                                article_data['date'].replace('Z', '+00:00')
                            )
                        except:
                            published_at = timezone.now()
                    
                    # Create article
                    article = NewsArticle.objects.create(
                        title=article_data.get('title', ''),
                        summary=article_data.get('text', ''),
                        content=article_data.get('text', ''),
                        url=article_data.get('news_url', ''),
                        image_url=article_data.get('image_url', '/static/images/news-placeholder.svg'),
                        published_at=published_at,
                        source=source,
                        category=category,
                        is_featured=i < 5,  # First 5 are featured
                        is_active=True,
                        tags=','.join(tickers[:5])
                    )
                    saved_count += 1
                    
                    if i < 3:  # Show first 3 articles
                        self.stdout.write(f"  {i+1}. {article.title[:50]}...")
                    
                except Exception as e:
                    self.stdout.write(f"Error saving crypto article {i+1}: {e}")
                    continue
            
            self.stdout.write(f"✅ Saved {saved_count} crypto articles to database")
            
        except Exception as e:
            self.stdout.write(f"❌ Crypto database error: {e}")
            import traceback
            traceback.print_exc()
