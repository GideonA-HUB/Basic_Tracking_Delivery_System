"""
Management command to fetch news from various APIs
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from investments.news_services import NewsAggregatorService
from investments.news_models import NewsSource, NewsCategory
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch news from various APIs and save to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Number of articles to fetch per category (default: 50)'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Specific category to fetch (crypto, stocks, real_estate, etc.)'
        )
        parser.add_argument(
            '--setup-sources',
            action='store_true',
            help='Setup default news sources and categories'
        )

    def handle(self, *args, **options):
        if options['setup_sources']:
            self.setup_default_sources()
            return

        limit = options['limit']
        category = options['category']

        self.stdout.write(
            self.style.SUCCESS('Starting news fetch process...')
        )

        try:
            # Initialize news aggregator
            aggregator = NewsAggregatorService()

            # Fetch news
            if category:
                self.stdout.write(f'Fetching {category} news...')
                articles = self.fetch_category_news(aggregator, category, limit)
            else:
                self.stdout.write('Fetching all news categories...')
                articles = aggregator.fetch_all_news(limit)

            # Save articles
            saved_count = aggregator.save_articles(articles)

            # Update featured news
            aggregator.update_featured_news()

            self.stdout.write(
                self.style.SUCCESS(
                    f'News fetch completed successfully!\n'
                    f'Articles fetched: {len(articles)}\n'
                    f'Articles saved: {saved_count}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching news: {str(e)}')
            )
            logger.error(f'News fetch error: {str(e)}')

    def fetch_category_news(self, aggregator, category, limit):
        """Fetch news for a specific category"""
        articles = []
        
        if category == 'crypto':
            # Try multiple crypto sources
            try:
                articles.extend(aggregator.services['crypto_coindesk'].get_crypto_news(limit//2))
            except:
                pass
            try:
                articles.extend(aggregator.services['crypto_cryptopanic'].get_crypto_news(limit//2))
            except:
                pass
        elif category == 'stocks':
            articles.extend(aggregator.services['general'].get_stock_news(limit))
        elif category == 'real_estate':
            articles.extend(aggregator.services['general'].get_real_estate_news(limit))
        else:
            self.stdout.write(
                self.style.WARNING(f'Unknown category: {category}')
            )
        
        return articles

    def setup_default_sources(self):
        """Setup default news sources and categories"""
        self.stdout.write('Setting up default news sources...')

        # Create news sources
        sources = [
            {
                'name': 'CoinDesk',
                'base_url': 'https://api.coindesk.com/v1',
                'is_active': True,
                'rate_limit_per_hour': 1000
            },
            {
                'name': 'CryptoPanic',
                'base_url': 'https://cryptopanic.com/api/developer/v2',
                'is_active': True,
                'rate_limit_per_hour': 1000
            },
            {
                'name': 'NewsAPI',
                'base_url': 'https://newsapi.org/v2',
                'is_active': True,
                'rate_limit_per_hour': 1000
            },
            {
                'name': 'Finnhub',
                'base_url': 'https://finnhub.io/api/v1',
                'is_active': True,
                'rate_limit_per_hour': 60
            }
        ]

        for source_data in sources:
            source, created = NewsSource.objects.get_or_create(
                name=source_data['name'],
                defaults=source_data
            )
            if created:
                self.stdout.write(f'Created news source: {source.name}')
            else:
                self.stdout.write(f'News source already exists: {source.name}')

        # Create news categories
        categories = [
            {'name': 'crypto', 'display_name': 'Cryptocurrency', 'description': 'Cryptocurrency news and updates'},
            {'name': 'stocks', 'display_name': 'Stock Market', 'description': 'Stock market news and analysis'},
            {'name': 'real_estate', 'display_name': 'Real Estate', 'description': 'Real estate market news'},
            {'name': 'forex', 'display_name': 'Forex', 'description': 'Foreign exchange market news'},
            {'name': 'commodities', 'display_name': 'Commodities', 'description': 'Commodities market news'},
            {'name': 'general', 'display_name': 'General Finance', 'description': 'General financial news'},
            {'name': 'bitcoin', 'display_name': 'Bitcoin', 'description': 'Bitcoin-specific news'},
            {'name': 'ethereum', 'display_name': 'Ethereum', 'description': 'Ethereum-specific news'},
            {'name': 'altcoins', 'display_name': 'Altcoins', 'description': 'Alternative cryptocurrency news'},
        ]

        for category_data in categories:
            category, created = NewsCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            if created:
                self.stdout.write(f'Created news category: {category.display_name}')
            else:
                self.stdout.write(f'News category already exists: {category.display_name}')

        self.stdout.write(
            self.style.SUCCESS('Default news sources and categories setup completed!')
        )
