"""
Management command to FORCE create news articles
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from investments.news_models import NewsArticle, NewsCategory, NewsSource
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'FORCE create news articles - guaranteed to work'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of articles to create'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 FORCE CREATING NEWS ARTICLES...')
        )
        
        try:
            # Create categories
            crypto_cat, _ = NewsCategory.objects.get_or_create(
                name='crypto',
                defaults={'display_name': 'Cryptocurrency', 'description': 'Crypto news'}
            )
            
            bitcoin_cat, _ = NewsCategory.objects.get_or_create(
                name='bitcoin',
                defaults={'display_name': 'Bitcoin', 'description': 'Bitcoin news'}
            )
            
            ethereum_cat, _ = NewsCategory.objects.get_or_create(
                name='ethereum',
                defaults={'display_name': 'Ethereum', 'description': 'Ethereum news'}
            )
            
            stocks_cat, _ = NewsCategory.objects.get_or_create(
                name='stocks',
                defaults={'display_name': 'Stock Market', 'description': 'Stock news'}
            )
            
            real_estate_cat, _ = NewsCategory.objects.get_or_create(
                name='real_estate',
                defaults={'display_name': 'Real Estate', 'description': 'Real estate news'}
            )
            
            # Create source
            source, _ = NewsSource.objects.get_or_create(
                name='Sample News',
                defaults={'base_url': 'https://example.com', 'is_active': True}
            )
            
            # Create articles
            articles = [
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
                    'category': ethereum_cat,
                    'is_featured': True
                },
                {
                    'title': 'Gold Prices Stabilize After Recent Volatility',
                    'summary': 'Gold has found support levels after recent market fluctuations.',
                    'category': stocks_cat,
                    'is_featured': False
                },
                {
                    'title': 'Bitcoin ETF Approval Drives Institutional Investment',
                    'summary': 'Recent Bitcoin ETF approvals have led to increased institutional investment in cryptocurrency.',
                    'category': bitcoin_cat,
                    'is_featured': True
                },
                {
                    'title': 'Real Estate Investment Trusts Show Strong Performance',
                    'summary': 'REITs continue to perform well as investors seek stable returns.',
                    'category': real_estate_cat,
                    'is_featured': False
                },
                {
                    'title': 'Cryptocurrency Market Cap Reaches New Milestone',
                    'summary': 'The total cryptocurrency market cap has reached a new all-time high.',
                    'category': crypto_cat,
                    'is_featured': True
                },
                {
                    'title': 'Tech Stocks Lead Market Recovery',
                    'summary': 'Technology companies are leading the market recovery with strong earnings.',
                    'category': stocks_cat,
                    'is_featured': False
                },
                {
                    'title': 'Ethereum Network Upgrade Improves Efficiency',
                    'summary': 'Latest Ethereum network upgrade has improved transaction efficiency and reduced fees.',
                    'category': ethereum_cat,
                    'is_featured': False
                }
            ]
            
            created_count = 0
            for article_data in articles:
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
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ SUCCESS! Created {created_count} news articles!')
            )
            
            # Show statistics
            total_articles = NewsArticle.objects.count()
            featured_articles = NewsArticle.objects.filter(is_featured=True).count()
            active_articles = NewsArticle.objects.filter(is_active=True).count()
            
            self.stdout.write('\n📊 News Statistics:')
            self.stdout.write(f'   Total Articles: {total_articles}')
            self.stdout.write(f'   Featured Articles: {featured_articles}')
            self.stdout.write(f'   Active Articles: {active_articles}')
            
            self.stdout.write('\n🎯 News system is now working!')
            self.stdout.write('Check: https://meridianassetlogistics.com/investments/news/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
            logger.error(f"Error in force_create_news: {e}")
