"""
Management command to create sample news data for testing
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from investments.news_models import NewsArticle, NewsSource, NewsCategory
from datetime import timedelta
import uuid


class Command(BaseCommand):
    help = 'Create sample news data for testing the news system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of sample articles to create (default: 20)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(
            self.style.SUCCESS('Creating sample news data...')
        )

        try:
            # Get or create news source
            source, created = NewsSource.objects.get_or_create(
                name='Sample News',
                defaults={
                    'base_url': 'https://example.com',
                    'is_active': True,
                    'rate_limit_per_hour': 1000
                }
            )

            # Get categories
            crypto_category = NewsCategory.objects.get(name='crypto')
            stocks_category = NewsCategory.objects.get(name='stocks')
            real_estate_category = NewsCategory.objects.get(name='real_estate')
            bitcoin_category = NewsCategory.objects.get(name='bitcoin')
            ethereum_category = NewsCategory.objects.get(name='ethereum')

            # Sample news data
            sample_articles = [
                {
                    'title': 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
                    'summary': 'Bitcoin has surged to new record levels as major corporations continue to add cryptocurrency to their balance sheets.',
                    'category': bitcoin_category,
                    'url': 'https://example.com/bitcoin-new-high',
                    'image_url': 'https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=400',
                    'is_featured': True
                },
                {
                    'title': 'Ethereum 2.0 Staking Rewards Hit Record Levels',
                    'summary': 'Ethereum stakers are seeing unprecedented returns as the network continues to evolve with new upgrades.',
                    'category': ethereum_category,
                    'url': 'https://example.com/ethereum-staking',
                    'image_url': 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400',
                    'is_featured': True
                },
                {
                    'title': 'Stock Market Rally Continues as Tech Stocks Lead Gains',
                    'summary': 'Major indices are up as technology companies report strong quarterly earnings and optimistic outlooks.',
                    'category': stocks_category,
                    'url': 'https://example.com/stock-rally',
                    'image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400',
                    'is_featured': True
                },
                {
                    'title': 'Real Estate Market Shows Signs of Cooling in Major Cities',
                    'summary': 'Housing prices are stabilizing as inventory levels increase and interest rates remain steady.',
                    'category': real_estate_category,
                    'url': 'https://example.com/real-estate-cooling',
                    'image_url': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400',
                    'is_featured': False
                },
                {
                    'title': 'Altcoin Season Begins as DeFi Tokens Surge',
                    'summary': 'Decentralized finance tokens are leading the altcoin rally as new protocols gain traction.',
                    'category': crypto_category,
                    'url': 'https://example.com/altcoin-season',
                    'image_url': 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=400',
                    'is_featured': False
                },
                {
                    'title': 'Federal Reserve Signals Potential Rate Cuts Ahead',
                    'summary': 'The Fed hints at possible monetary policy changes as inflation concerns ease.',
                    'category': stocks_category,
                    'url': 'https://example.com/fed-rate-cuts',
                    'image_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400',
                    'is_featured': False
                },
                {
                    'title': 'Commercial Real Estate Investment Reaches New Heights',
                    'summary': 'Investors are pouring money into commercial properties as yields remain attractive.',
                    'category': real_estate_category,
                    'url': 'https://example.com/commercial-real-estate',
                    'image_url': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400',
                    'is_featured': False
                },
                {
                    'title': 'Cryptocurrency Regulation Framework Takes Shape',
                    'summary': 'New regulatory guidelines provide clarity for crypto businesses and investors.',
                    'category': crypto_category,
                    'url': 'https://example.com/crypto-regulation',
                    'image_url': 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400',
                    'is_featured': False
                },
                {
                    'title': 'Tech Giants Report Strong Q4 Earnings',
                    'summary': 'Major technology companies exceed expectations with robust revenue growth.',
                    'category': stocks_category,
                    'url': 'https://example.com/tech-earnings',
                    'image_url': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400',
                    'is_featured': False
                },
                {
                    'title': 'Bitcoin Mining Difficulty Adjusts to New Network Conditions',
                    'summary': 'The Bitcoin network has adjusted its mining difficulty to maintain optimal block times.',
                    'category': bitcoin_category,
                    'url': 'https://example.com/bitcoin-mining-difficulty',
                    'image_url': 'https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=400',
                    'is_featured': False
                },
                {
                    'title': 'Ethereum Gas Fees Drop to Lowest Levels in Months',
                    'summary': 'Network congestion has eased, resulting in significantly lower transaction costs.',
                    'category': ethereum_category,
                    'url': 'https://example.com/ethereum-gas-fees',
                    'image_url': 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400',
                    'is_featured': False
                },
                {
                    'title': 'Housing Market Inventory Increases Across Major Metros',
                    'summary': 'More homes are coming to market as sellers take advantage of current prices.',
                    'category': real_estate_category,
                    'url': 'https://example.com/housing-inventory',
                    'image_url': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400',
                    'is_featured': False
                },
                {
                    'title': 'DeFi Total Value Locked Surpasses $100 Billion',
                    'summary': 'Decentralized finance protocols continue to attract significant capital inflows.',
                    'category': crypto_category,
                    'url': 'https://example.com/defi-tvl',
                    'image_url': 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=400',
                    'is_featured': False
                },
                {
                    'title': 'Energy Sector Stocks Rally on Oil Price Recovery',
                    'summary': 'Energy companies see strong performance as commodity prices stabilize.',
                    'category': stocks_category,
                    'url': 'https://example.com/energy-stocks',
                    'image_url': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400',
                    'is_featured': False
                },
                {
                    'title': 'Real Estate Investment Trusts Show Strong Performance',
                    'summary': 'REITs are outperforming broader markets as property values remain stable.',
                    'category': real_estate_category,
                    'url': 'https://example.com/reits-performance',
                    'image_url': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400',
                    'is_featured': False
                }
            ]

            # Create articles
            created_count = 0
            for i, article_data in enumerate(sample_articles[:count]):
                # Create unique published dates (spread over last 7 days)
                published_at = timezone.now() - timedelta(
                    hours=i * 2,  # 2 hours apart
                    minutes=i * 15  # 15 minutes apart
                )

                article = NewsArticle.objects.create(
                    title=article_data['title'],
                    summary=article_data['summary'],
                    url=article_data['url'],
                    image_url=article_data['image_url'],
                    published_at=published_at,
                    source=source,
                    category=article_data['category'],
                    author='Sample News',
                    tags=['sample', 'test'],
                    is_featured=article_data['is_featured'],
                    is_active=True
                )
                created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Successfully created {created_count} sample news articles!'
                )
            )

            self.stdout.write('\n📊 Sample Data Summary:')
            self.stdout.write(f'   Total Articles: {NewsArticle.objects.count()}')
            self.stdout.write(f'   Featured Articles: {NewsArticle.objects.filter(is_featured=True).count()}')
            self.stdout.write(f'   Active Articles: {NewsArticle.objects.filter(is_active=True).count()}')

            self.stdout.write('\n🎯 Next Steps:')
            self.stdout.write('1. Test the news system: /investments/news/')
            self.stdout.write('2. Check dashboard widgets')
            self.stdout.write('3. Add real API keys when ready')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating sample news: {str(e)}')
            )
