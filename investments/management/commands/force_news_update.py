"""
Management command to force news update on Railway
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from investments.news_services import NewsAggregator
from investments.news_models import NewsArticle
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Force news update - fetch from APIs and clear old data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Clear all existing news before fetching new ones'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of articles per category'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 FORCING NEWS UPDATE ON RAILWAY...')
        )
        
        # Clear all news if requested
        if options['clear_all']:
            self.stdout.write('🗑️  Clearing all existing news...')
            NewsArticle.objects.all().delete()
            self.stdout.write('✅ All news cleared')
        
        # Initialize news aggregator
        aggregator = NewsAggregator()
        
        # Check configured services
        configured_services = aggregator.get_configured_services()
        self.stdout.write(f'🔑 Configured services: {configured_services}')
        
        if not configured_services:
            self.stdout.write(
                self.style.ERROR('❌ NO API KEYS CONFIGURED!')
            )
            self.stdout.write('Please check your Railway environment variables:')
            self.stdout.write('- NEWSAPI_KEY')
            self.stdout.write('- FINNHUB_API_KEY')
            self.stdout.write('- CRYPTOPANIC_API_KEY')
            self.stdout.write('- COINDESK_API_KEY')
            return
        
        # Force fetch news
        categories = ['crypto', 'bitcoin', 'stocks', 'real_estate', 'ethereum', 'altcoins']
        count_per_category = options['count']
        
        self.stdout.write(f"📰 Fetching news for categories: {', '.join(categories)}")
        self.stdout.write(f"📊 Target: {count_per_category} articles per category")
        
        try:
            articles = aggregator.fetch_all_news(categories, count_per_category)
            
            if articles:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ SUCCESS! Fetched {len(articles)} articles!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  No new articles fetched. Trying with sample data...')
                )
                # Create some sample articles if APIs fail
                self.create_sample_articles()
            
            # Show final statistics
            stats = aggregator.get_news_stats()
            self.stdout.write('\n📊 FINAL NEWS STATISTICS:')
            self.stdout.write(f'   Total Articles: {stats["total_articles"]}')
            self.stdout.write(f'   Featured Articles: {stats["featured_articles"]}')
            self.stdout.write(f'   Active Articles: {stats["active_articles"]}')
            
            self.stdout.write('\n📂 By Category:')
            for category, count in stats['by_category'].items():
                if count > 0:
                    self.stdout.write(f'   {category}: {count} articles')
            
            self.stdout.write('\n📰 By Source:')
            for source, count in stats['by_source'].items():
                if count > 0:
                    self.stdout.write(f'   {source}: {count} articles')
            
            self.stdout.write('\n🎯 NEWS SYSTEM IS NOW ACTIVE!')
            self.stdout.write('Check: https://meridianassetlogistics.com/investments/news/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
            logger.error(f"Error in force_news_update: {e}")
            
            # Create sample articles as fallback
            self.stdout.write('Creating sample articles as fallback...')
            self.create_sample_articles()
    
    def create_sample_articles(self):
        """Create sample articles if APIs fail"""
        from investments.news_models import NewsCategory, NewsSource
        
        # Get or create categories
        crypto_cat, _ = NewsCategory.objects.get_or_create(
            name='crypto',
            defaults={'display_name': 'Cryptocurrency', 'description': 'Crypto news'}
        )
        
        stocks_cat, _ = NewsCategory.objects.get_or_create(
            name='stocks',
            defaults={'display_name': 'Stock Market', 'description': 'Stock news'}
        )
        
        real_estate_cat, _ = NewsCategory.objects.get_or_create(
            name='real_estate',
            defaults={'display_name': 'Real Estate', 'description': 'Real estate news'}
        )
        
        # Get or create source
        source, _ = NewsSource.objects.get_or_create(
            name='Sample News',
            defaults={'base_url': 'https://example.com', 'is_active': True}
        )
        
        # Create sample articles
        sample_articles = [
            {
                'title': 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
                'summary': 'Bitcoin has surged to new record levels as major institutions continue to adopt cryptocurrency.',
                'category': crypto_cat,
                'is_featured': True
            },
            {
                'title': 'Stock Market Rally Continues as Tech Stocks Lead Gains',
                'summary': 'Major indices are up as technology companies report strong quarterly earnings.',
                'category': stocks_cat,
                'is_featured': True
            },
            {
                'title': 'Real Estate Market Shows Strong Growth in Q4',
                'summary': 'Property values continue to rise across major metropolitan areas.',
                'category': real_estate_cat,
                'is_featured': False
            },
            {
                'title': 'Ethereum 2.0 Staking Rewards Hit Record Levels',
                'summary': 'Ethereum staking rewards have reached new highs as the network continues to grow.',
                'category': crypto_cat,
                'is_featured': True
            },
            {
                'title': 'Gold Prices Stabilize After Recent Volatility',
                'summary': 'Gold has found support levels after recent market fluctuations.',
                'category': stocks_cat,
                'is_featured': False
            }
        ]
        
        created_count = 0
        for article_data in sample_articles:
            if not NewsArticle.objects.filter(title=article_data['title']).exists():
                NewsArticle.objects.create(
                    title=article_data['title'],
                    summary=article_data['summary'],
                    content=article_data['summary'],
                    source=source,
                    category=article_data['category'],
                    is_featured=article_data['is_featured'],
                    is_active=True,
                    published_at=timezone.now()
                )
                created_count += 1
        
        self.stdout.write(f'✅ Created {created_count} sample articles')
