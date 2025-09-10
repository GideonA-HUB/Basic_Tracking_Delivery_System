"""
Management command to force API news fetching with detailed debugging
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from investments.news_services import NewsAggregator
from investments.news_models import NewsArticle
import requests
import json

class Command(BaseCommand):
    help = 'Force fetch news from APIs with detailed debugging'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of articles to fetch per category'
        )
        parser.add_argument(
            '--test-apis',
            action='store_true',
            help='Test API calls directly before fetching'
        )

    def handle(self, *args, **options):
        count = options['count']
        test_apis = options['test_apis']
        
        self.stdout.write("🚀 FORCING API NEWS FETCH...")
        
        # Test API keys first
        self.stdout.write("\n🔑 CHECKING API KEYS...")
        self.stdout.write(f"NEWSAPI_KEY: {'✅ Set' if settings.NEWSAPI_KEY else '❌ Not Set'}")
        self.stdout.write(f"FINNHUB_API_KEY: {'✅ Set' if settings.FINNHUB_API_KEY else '❌ Not Set'}")
        self.stdout.write(f"CRYPTOPANIC_API_KEY: {'✅ Set' if settings.CRYPTOPANIC_API_KEY else '❌ Not Set'}")
        self.stdout.write(f"COINDESK_API_KEY: {'✅ Set' if settings.COINDESK_API_KEY else '❌ Not Set'}")
        
        if test_apis:
            self.test_apis_directly()
        
        # Clear existing news
        current_count = NewsArticle.objects.count()
        self.stdout.write(f"\n📊 Current articles in database: {current_count}")
        
        if current_count > 0:
            self.stdout.write("🗑️  Clearing existing news...")
            NewsArticle.objects.all().delete()
        
        # Try to fetch from APIs
        self.stdout.write("\n🔄 ATTEMPTING API FETCH...")
        try:
            aggregator = NewsAggregator()
            configured_services = aggregator.get_configured_services()
            self.stdout.write(f"Configured services: {configured_services}")
            
            if not configured_services:
                self.stdout.write("❌ NO CONFIGURED SERVICES!")
                self.stdout.write("This means API keys are not being loaded properly.")
                return
            
            # Fetch news
            articles = aggregator.fetch_all_news(['crypto', 'stocks', 'real_estate'], count)
            self.stdout.write(f"✅ Fetched {len(articles)} articles from APIs")
            
            if articles:
                # Save articles
                saved_count = aggregator.save_articles(articles)
                self.stdout.write(f"✅ Saved {saved_count} articles to database")
                
                # Show sample
                self.stdout.write("\n📰 Sample articles:")
                for i, article in enumerate(articles[:3]):
                    self.stdout.write(f"  {i+1}. {article.get('title', 'No title')}")
            else:
                self.stdout.write("⚠️  No articles returned from APIs")
                
        except Exception as e:
            self.stdout.write(f"❌ Error fetching from APIs: {e}")
            import traceback
            traceback.print_exc()
        
        # Show final statistics
        final_count = NewsArticle.objects.count()
        self.stdout.write(f"\n📊 FINAL STATS: {final_count} articles in database")
        
        if final_count == 0:
            self.stdout.write("⚠️  No articles in database - creating fallback...")
            self.create_fallback_news()

    def test_apis_directly(self):
        """Test API calls directly"""
        self.stdout.write("\n🌐 TESTING APIs DIRECTLY...")
        
        # Test NewsAPI
        if settings.NEWSAPI_KEY:
            self.stdout.write("Testing NewsAPI...")
            try:
                url = f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={settings.NEWSAPI_KEY}"
                response = requests.get(url, timeout=10)
                self.stdout.write(f"NewsAPI Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    self.stdout.write(f"NewsAPI Articles: {len(data.get('articles', []))}")
                else:
                    self.stdout.write(f"NewsAPI Error: {response.text[:100]}")
            except Exception as e:
                self.stdout.write(f"NewsAPI Exception: {e}")
        
        # Test Finnhub
        if settings.FINNHUB_API_KEY:
            self.stdout.write("Testing Finnhub...")
            try:
                url = f"https://finnhub.io/api/v1/news?category=general&token={settings.FINNHUB_API_KEY}"
                response = requests.get(url, timeout=10)
                self.stdout.write(f"Finnhub Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    self.stdout.write(f"Finnhub Articles: {len(data) if isinstance(data, list) else 'Not a list'}")
                else:
                    self.stdout.write(f"Finnhub Error: {response.text[:100]}")
            except Exception as e:
                self.stdout.write(f"Finnhub Exception: {e}")

    def create_fallback_news(self):
        """Create fallback news if APIs fail"""
        try:
            from investments.news_models import NewsCategory, NewsSource
            from django.utils import timezone
            
            # Create categories
            crypto_cat, _ = NewsCategory.objects.get_or_create(
                name='crypto',
                defaults={'display_name': 'Cryptocurrency', 'description': 'Crypto news'}
            )
            
            # Create source
            source, _ = NewsSource.objects.get_or_create(
                name='Fallback News',
                defaults={'base_url': 'https://fallback.com', 'is_active': True}
            )
            
            # Create fallback articles
            fallback_articles = [
                {
                    'title': 'Bitcoin Reaches New All-Time High',
                    'summary': 'Bitcoin has surged to unprecedented levels as institutional adoption continues.',
                    'is_featured': True
                },
                {
                    'title': 'Stock Market Shows Strong Performance',
                    'summary': 'Major indices are up as technology companies report strong earnings.',
                    'is_featured': True
                },
                {
                    'title': 'Real Estate Market Continues Growth',
                    'summary': 'Property values continue to rise across major metropolitan areas.',
                    'is_featured': False
                }
            ]
            
            created_count = 0
            for article_data in fallback_articles:
                NewsArticle.objects.create(
                    title=article_data['title'],
                    summary=article_data['summary'],
                    content=article_data['summary'],
                    source=source,
                    category=crypto_cat,
                    is_featured=article_data['is_featured'],
                    is_active=True,
                    published_at=timezone.now()
                )
                created_count += 1
            
            self.stdout.write(f"✅ Created {created_count} fallback articles")
            
        except Exception as e:
            self.stdout.write(f"❌ Error creating fallback news: {e}")
