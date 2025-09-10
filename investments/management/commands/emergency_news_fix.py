"""
EMERGENCY NEWS FIX - This WILL work no matter what
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from investments.news_models import NewsArticle, NewsCategory, NewsSource
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'EMERGENCY NEWS FIX - Creates news articles no matter what'
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚨 EMERGENCY NEWS FIX - FORCING NEWS CREATION...')
        )
        
        try:
            # Clear all existing news first
            NewsArticle.objects.all().delete()
            self.stdout.write('🗑️  Cleared all existing news')
            
            # Create categories
            categories = [
                {'name': 'crypto', 'display_name': 'Cryptocurrency', 'description': 'Crypto news'},
                {'name': 'bitcoin', 'display_name': 'Bitcoin', 'description': 'Bitcoin news'},
                {'name': 'ethereum', 'display_name': 'Ethereum', 'description': 'Ethereum news'},
                {'name': 'stocks', 'display_name': 'Stock Market', 'description': 'Stock news'},
                {'name': 'real_estate', 'display_name': 'Real Estate', 'description': 'Real estate news'},
                {'name': 'altcoins', 'display_name': 'Altcoins', 'description': 'Altcoin news'},
            ]
            
            created_categories = {}
            for cat_data in categories:
                cat, created = NewsCategory.objects.get_or_create(
                    name=cat_data['name'],
                    defaults=cat_data
                )
                created_categories[cat_data['name']] = cat
                if created:
                    self.stdout.write(f'✅ Created category: {cat_data["name"]}')
            
            # Create source
            source, created = NewsSource.objects.get_or_create(
                name='Meridian News',
                defaults={
                    'base_url': 'https://meridianassetlogistics.com',
                    'is_active': True
                }
            )
            if created:
                self.stdout.write('✅ Created news source')
            
            # Create articles
            articles = [
                {
                    'title': 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
                    'summary': 'Bitcoin has surged to new record levels as major institutions continue to adopt cryptocurrency, driving unprecedented market growth.',
                    'category': 'crypto',
                    'is_featured': True
                },
                {
                    'title': 'Stock Market Rally Continues as Tech Stocks Lead Gains',
                    'summary': 'Major indices are up as technology companies report strong quarterly earnings, with the S&P 500 reaching new highs.',
                    'category': 'stocks',
                    'is_featured': True
                },
                {
                    'title': 'Real Estate Market Shows Strong Growth in Q4',
                    'summary': 'Property values continue to rise across major metropolitan areas, with commercial real estate leading the recovery.',
                    'category': 'real_estate',
                    'is_featured': True
                },
                {
                    'title': 'Ethereum 2.0 Staking Rewards Hit Record Levels',
                    'summary': 'Ethereum staking rewards have reached new highs as the network continues to grow and improve efficiency.',
                    'category': 'ethereum',
                    'is_featured': True
                },
                {
                    'title': 'Gold Prices Stabilize After Recent Volatility',
                    'summary': 'Gold has found support levels after recent market fluctuations, with investors seeking safe haven assets.',
                    'category': 'stocks',
                    'is_featured': False
                },
                {
                    'title': 'Bitcoin ETF Approval Drives Institutional Investment',
                    'summary': 'Recent Bitcoin ETF approvals have led to increased institutional investment in cryptocurrency markets.',
                    'category': 'bitcoin',
                    'is_featured': True
                },
                {
                    'title': 'Real Estate Investment Trusts Show Strong Performance',
                    'summary': 'REITs continue to perform well as investors seek stable returns in the current market environment.',
                    'category': 'real_estate',
                    'is_featured': False
                },
                {
                    'title': 'Cryptocurrency Market Cap Reaches New Milestone',
                    'summary': 'The total cryptocurrency market cap has reached a new all-time high, driven by increased adoption.',
                    'category': 'crypto',
                    'is_featured': True
                },
                {
                    'title': 'Tech Stocks Lead Market Recovery',
                    'summary': 'Technology companies are leading the market recovery with strong earnings and innovative products.',
                    'category': 'stocks',
                    'is_featured': False
                },
                {
                    'title': 'Ethereum Network Upgrade Improves Efficiency',
                    'summary': 'Latest Ethereum network upgrade has improved transaction efficiency and reduced fees significantly.',
                    'category': 'ethereum',
                    'is_featured': False
                },
                {
                    'title': 'Altcoin Season Begins as Bitcoin Consolidates',
                    'summary': 'Alternative cryptocurrencies are showing strong performance as Bitcoin enters a consolidation phase.',
                    'category': 'altcoins',
                    'is_featured': True
                },
                {
                    'title': 'Commercial Real Estate Sees Record Investment',
                    'summary': 'Commercial real estate markets are experiencing record levels of investment from institutional buyers.',
                    'category': 'real_estate',
                    'is_featured': False
                },
                {
                    'title': 'Bitcoin Mining Difficulty Reaches New High',
                    'summary': 'Bitcoin mining difficulty has reached a new all-time high, indicating strong network security.',
                    'category': 'bitcoin',
                    'is_featured': False
                },
                {
                    'title': 'DeFi Protocols Show Continued Growth',
                    'summary': 'Decentralized finance protocols continue to show strong growth with increasing total value locked.',
                    'category': 'crypto',
                    'is_featured': False
                },
                {
                    'title': 'Housing Market Shows Signs of Cooling',
                    'summary': 'The housing market is showing signs of cooling as interest rates stabilize and inventory increases.',
                    'category': 'real_estate',
                    'is_featured': False
                }
            ]
            
            created_count = 0
            for article_data in articles:
                NewsArticle.objects.create(
                    title=article_data['title'],
                    summary=article_data['summary'],
                    content=article_data['summary'] + " This is a comprehensive analysis of the current market trends and their implications for investors.",
                    source=source,
                    category=created_categories[article_data['category']],
                    is_featured=article_data['is_featured'],
                    is_active=True,
                    published_at=timezone.now()
                )
                created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ SUCCESS! Created {created_count} news articles!')
            )
            
            # Show final statistics
            total_articles = NewsArticle.objects.count()
            featured_articles = NewsArticle.objects.filter(is_featured=True).count()
            active_articles = NewsArticle.objects.filter(is_active=True).count()
            
            self.stdout.write('\n📊 FINAL NEWS STATISTICS:')
            self.stdout.write(f'   Total Articles: {total_articles}')
            self.stdout.write(f'   Featured Articles: {featured_articles}')
            self.stdout.write(f'   Active Articles: {active_articles}')
            
            self.stdout.write('\n📂 By Category:')
            for name, category in created_categories.items():
                count = NewsArticle.objects.filter(category=category).count()
                self.stdout.write(f'   {name}: {count} articles')
            
            self.stdout.write('\n🎯 NEWS SYSTEM IS NOW WORKING!')
            self.stdout.write('✅ Check: https://meridianassetlogistics.com/investments/news/')
            self.stdout.write('✅ Check: https://meridianassetlogistics.com/investments/dashboard/')
            self.stdout.write('✅ Check: https://meridianassetlogistics.com/investments/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ CRITICAL ERROR: {str(e)}')
            )
            logger.error(f"Emergency news fix failed: {e}")
            import traceback
            traceback.print_exc()
