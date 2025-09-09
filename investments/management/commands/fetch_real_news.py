"""
Management command to fetch real news from APIs
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from investments.news_services import NewsAggregator
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch real news from configured APIs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            nargs='+',
            default=['crypto', 'bitcoin', 'stocks', 'real_estate'],
            help='Categories to fetch news for'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of articles per category'
        )
        parser.add_argument(
            '--clear-old',
            action='store_true',
            help='Clear old articles before fetching new ones'
        )
        parser.add_argument(
            '--days-old',
            type=int,
            default=7,
            help='Clear articles older than this many days (when using --clear-old)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting real news fetch from APIs...')
        )
        
        # Clear old articles if requested
        if options['clear_old']:
            self.clear_old_articles(options['days_old'])
        
        # Initialize news aggregator
        aggregator = NewsAggregator()
        
        # Check configured services
        configured_services = aggregator.get_configured_services()
        if not configured_services:
            self.stdout.write(
                self.style.WARNING('⚠️  No API keys configured. Using sample data only.')
            )
            self.stdout.write('💡 To use real APIs, set these environment variables:')
            self.stdout.write('   - NEWSAPI_KEY')
            self.stdout.write('   - FINNHUB_API_KEY') 
            self.stdout.write('   - CRYPTOPANIC_API_KEY')
            self.stdout.write('   - COINDESK_API_KEY')
            self.stdout.write('\n📊 Current sample data statistics:')
            stats = aggregator.get_news_stats()
            self.stdout.write(f'   Total Articles: {stats["total_articles"]}')
            self.stdout.write(f'   Featured Articles: {stats["featured_articles"]}')
            self.stdout.write(f'   Active Articles: {stats["active_articles"]}')
            return
        
        self.stdout.write(f'🔑 Configured services: {", ".join(configured_services)}')
        
        # Fetch news
        categories = options['categories']
        count_per_category = options['count']
        
        self.stdout.write(f"📰 Fetching news for categories: {', '.join(categories)}")
        self.stdout.write(f"📊 Target: {count_per_category} articles per category")
        
        try:
            articles = aggregator.fetch_all_news(categories, count_per_category)
            
            if articles:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Successfully fetched {len(articles)} articles!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  No new articles fetched. This could be due to:')
                )
                self.stdout.write('   - Rate limiting from APIs')
                self.stdout.write('   - Network connectivity issues')
                self.stdout.write('   - API key restrictions')
                self.stdout.write('   - All articles already exist in database')
            
            # Show statistics
            stats = aggregator.get_news_stats()
            self.stdout.write('\n📊 News Statistics:')
            self.stdout.write(f'   Total Articles: {stats["total_articles"]}')
            self.stdout.write(f'   Featured Articles: {stats["featured_articles"]}')
            self.stdout.write(f'   Active Articles: {stats["active_articles"]}')
            
            self.stdout.write('\n📂 By Category:')
            for category, count in stats['by_category'].items():
                self.stdout.write(f'   {category}: {count} articles')
            
            self.stdout.write('\n📰 By Source:')
            for source, count in stats['by_source'].items():
                self.stdout.write(f'   {source}: {count} articles')
            
            self.stdout.write('\n🎯 Next Steps:')
            self.stdout.write('1. Check the news dashboard: /investments/news/')
            self.stdout.write('2. View news widgets on other pages')
            self.stdout.write('3. Manage news in Django admin: /admin/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error fetching news: {str(e)}')
            )
            logger.error(f"Error in fetch_real_news command: {e}")
    
    def clear_old_articles(self, days_old):
        """Clear articles older than specified days"""
        from investments.news_models import NewsArticle
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days_old)
        old_articles = NewsArticle.objects.filter(created_at__lt=cutoff_date)
        count = old_articles.count()
        
        if count > 0:
            old_articles.delete()
            self.stdout.write(
                self.style.WARNING(f'🗑️  Cleared {count} articles older than {days_old} days')
            )
        else:
            self.stdout.write('ℹ️  No old articles to clear')
