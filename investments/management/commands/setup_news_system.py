"""
Management command to set up the news system
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from investments.news_models import NewsSource, NewsCategory
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up the complete news system with sources, categories, and initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fetch-initial-news',
            action='store_true',
            help='Fetch initial news after setup'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up News Integration System...')
        )

        try:
            # Step 1: Setup news sources and categories
            self.stdout.write('📰 Setting up news sources and categories...')
            call_command('fetch_news', '--setup-sources')
            
            # Step 2: Create database tables
            self.stdout.write('🗄️ Creating database tables...')
            call_command('makemigrations', 'investments')
            call_command('migrate', 'investments')
            
            # Step 3: Fetch initial news if requested
            if options['fetch_initial_news']:
                self.stdout.write('📡 Fetching initial news...')
                call_command('fetch_news', '--limit', '30')
            
            # Step 4: Display setup summary
            self.display_setup_summary()
            
            self.stdout.write(
                self.style.SUCCESS('✅ News Integration System setup completed successfully!')
            )
            
            self.stdout.write('\n📋 Next Steps:')
            self.stdout.write('1. Add API keys to your environment variables:')
            self.stdout.write('   - NEWSAPI_KEY=your_newsapi_key')
            self.stdout.write('   - FINNHUB_API_KEY=your_finnhub_key')
            self.stdout.write('   - COINDESK_API_KEY=your_coindesk_key')
            self.stdout.write('   - CRYPTOPANIC_API_KEY=your_cryptopanic_key (optional)')
            self.stdout.write('2. Set up a cron job to fetch news regularly:')
            self.stdout.write('   */15 * * * * python manage.py fetch_news')
            self.stdout.write('3. Access the news dashboard at: /investments/news/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error setting up news system: {str(e)}')
            )
            logger.error(f'News system setup error: {str(e)}')

    def display_setup_summary(self):
        """Display setup summary"""
        sources_count = NewsSource.objects.count()
        categories_count = NewsCategory.objects.count()
        
        self.stdout.write('\n📊 Setup Summary:')
        self.stdout.write(f'   News Sources: {sources_count}')
        self.stdout.write(f'   News Categories: {categories_count}')
        
        self.stdout.write('\n🔗 Available News Sources:')
        for source in NewsSource.objects.all():
            status = '✅ Active' if source.is_active else '❌ Inactive'
            self.stdout.write(f'   - {source.name}: {status}')
        
        self.stdout.write('\n📂 Available Categories:')
        for category in NewsCategory.objects.all():
            status = '✅ Active' if category.is_active else '❌ Inactive'
            self.stdout.write(f'   - {category.display_name}: {status}')
