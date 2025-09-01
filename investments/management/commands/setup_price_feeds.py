from django.core.management.base import BaseCommand
from django.utils import timezone
from investments.models import RealTimePriceFeed
from investments.price_services import price_service
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Set up real-time price feeds for various assets'

    def handle(self, *args, **options):
        self.stdout.write('Setting up real-time price feeds...')
        
        # Define price feeds to create
        price_feeds = [
            {
                'name': 'Bitcoin',
                'asset_type': 'crypto',
                'symbol': 'BTC',
                'current_price': 45000.00,
                'api_source': 'CoinGecko',
                'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
            },
            {
                'name': 'Ethereum',
                'asset_type': 'crypto',
                'symbol': 'ETH',
                'current_price': 3000.00,
                'api_source': 'CoinGecko',
                'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
            },
            {
                'name': 'Cardano',
                'asset_type': 'crypto',
                'symbol': 'ADA',
                'current_price': 0.50,
                'api_source': 'CoinGecko',
                'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=cardano&vs_currencies=usd'
            },
            {
                'name': 'Gold (1 oz)',
                'asset_type': 'gold',
                'symbol': 'XAU',
                'current_price': 2000.00,
                'api_source': 'Metals API',
                'api_url': 'https://api.metals.live/v1/spot'
            },
            {
                'name': 'Silver (1 oz)',
                'asset_type': 'silver',
                'symbol': 'XAG',
                'current_price': 25.00,
                'api_source': 'Metals API',
                'api_url': 'https://api.metals.live/v1/spot'
            },
            {
                'name': 'Platinum (1 oz)',
                'asset_type': 'platinum',
                'symbol': 'XPT',
                'current_price': 1000.00,
                'api_source': 'Metals API',
                'api_url': 'https://api.metals.live/v1/spot'
            },
            {
                'name': 'Real Estate Index',
                'asset_type': 'real_estate',
                'symbol': 'REIT_INDEX',
                'current_price': 1500.00,
                'api_source': 'Simulated',
                'api_url': ''
            },
            {
                'name': 'Property Fund',
                'asset_type': 'real_estate',
                'symbol': 'PROPERTY_FUND',
                'current_price': 2500.00,
                'api_source': 'Simulated',
                'api_url': ''
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for feed_data in price_feeds:
            feed, created = RealTimePriceFeed.objects.get_or_create(
                symbol=feed_data['symbol'],
                defaults={
                    'name': feed_data['name'],
                    'asset_type': feed_data['asset_type'],
                    'current_price': feed_data['current_price'],
                    'api_source': feed_data['api_source'],
                    'api_url': feed_data['api_url'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created price feed: {feed.name} ({feed.symbol})')
            else:
                # Update existing feed
                feed.name = feed_data['name']
                feed.asset_type = feed_data['asset_type']
                feed.api_source = feed_data['api_source']
                feed.api_url = feed_data['api_url']
                feed.is_active = True
                feed.save()
                updated_count += 1
                self.stdout.write(f'Updated price feed: {feed.name} ({feed.symbol})')
        
        # Update all prices with real data
        self.stdout.write('Updating prices with real data...')
        updated_prices = price_service.update_all_prices()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up {created_count} new price feeds, '
                f'updated {updated_count} existing feeds, '
                f'and updated {updated_prices} prices with real data.'
            )
        )
