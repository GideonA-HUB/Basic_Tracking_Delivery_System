from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from investments.models import InvestmentItem, RealTimePriceFeed

class Command(BaseCommand):
    help = 'Fix production database issues for live price updates'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 FIXING PRODUCTION DATABASE ON RAILWAY')
        )
        self.stdout.write('=' * 60)
        
        # Step 1: Fix missing last_price_update fields
        self.stdout.write('\n🔧 STEP 1: Fixing missing last_price_update fields...')
        items = InvestmentItem.objects.all()
        self.stdout.write(f"Found {items.count()} investment items")
        
        fixed_count = 0
        for item in items:
            if not hasattr(item, 'last_price_update') or item.last_price_update is None:
                item.last_price_update = timezone.now()
                item.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Fixed {item.name}: Added last_price_update")
                )
                fixed_count += 1
            else:
                self.stdout.write(f"ℹ️  {item.name}: Already has last_price_update")
        
        self.stdout.write(
            self.style.SUCCESS(f"🎯 Fixed {fixed_count} items with missing last_price_update")
        )
        
        # Step 2: Create missing price feeds
        self.stdout.write('\n🔧 STEP 2: Creating missing price feeds...')
        self.create_price_feeds()
        
        # Step 3: Update items with symbols
        self.stdout.write('\n🔧 STEP 3: Updating items with symbols...')
        self.update_items_with_symbols()
        
        # Step 4: Verify fixes
        self.stdout.write('\n🔍 STEP 4: Verifying fixes...')
        self.verify_fixes()
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 PRODUCTION DATABASE FIX COMPLETED!')
        )
        self.stdout.write('💡 Your live price updates should now work!')

    def create_price_feeds(self):
        """Create all required price feeds"""
        required_feeds = [
            {
                'name': 'Bitcoin',
                'asset_type': 'crypto',
                'symbol': 'BTC',
                'current_price': Decimal('45000.00'),
                'api_source': 'CoinGecko',
                'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
            },
            {
                'name': 'Ethereum',
                'asset_type': 'crypto',
                'symbol': 'ETH',
                'current_price': Decimal('3000.00'),
                'api_source': 'CoinGecko',
                'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
            },
            {
                'name': 'Cardano',
                'asset_type': 'crypto',
                'symbol': 'ADA',
                'current_price': Decimal('0.50'),
                'api_source': 'CoinGecko',
                'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=cardano&vs_currencies=usd'
            },
            {
                'name': 'Gold (1 oz)',
                'asset_type': 'gold',
                'symbol': 'XAU',
                'current_price': Decimal('2000.00'),
                'api_source': 'Metals API',
                'api_url': 'https://api.metals.live/v1/spot'
            },
            {
                'name': 'Silver (1 oz)',
                'asset_type': 'silver',
                'symbol': 'XAG',
                'current_price': Decimal('25.00'),
                'api_source': 'Metals API',
                'api_url': 'https://api.metals.live/v1/spot'
            },
            {
                'name': 'Platinum (1 oz)',
                'asset_type': 'platinum',
                'symbol': 'XPT',
                'current_price': Decimal('1000.00'),
                'api_source': 'Metals API',
                'api_url': 'https://api.metals.live/v1/spot'
            },
            {
                'name': 'Real Estate Index',
                'asset_type': 'real_estate',
                'symbol': 'REIT_INDEX',
                'current_price': Decimal('1500.00'),
                'api_source': 'Simulated',
                'api_url': ''
            },
            {
                'name': 'Property Fund',
                'asset_type': 'real_estate',
                'symbol': 'PROPERTY_FUND',
                'current_price': Decimal('2500.00'),
                'api_source': 'Simulated',
                'api_url': ''
            }
        ]
        
        created_count = 0
        for feed_data in required_feeds:
            feed, created = RealTimePriceFeed.objects.get_or_create(
                symbol=feed_data['symbol'],
                defaults={
                    'name': feed_data['name'],
                    'asset_type': feed_data['asset_type'],
                    'current_price': feed_data['current_price'],
                    'api_source': feed_data['api_source'],
                    'api_url': feed_data['api_url'],
                    'is_active': True,
                    'last_updated': timezone.now()
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Created price feed: {feed.name} ({feed.symbol})")
                )
                created_count += 1
            else:
                self.stdout.write(f"ℹ️  Price feed already exists: {feed.name} ({feed.symbol})")
        
        self.stdout.write(
            self.style.SUCCESS(f"🎯 Total price feeds: {RealTimePriceFeed.objects.count()}")
        )

    def update_items_with_symbols(self):
        """Update items to have proper symbols"""
        symbol_mappings = {
            'Bitcoin (BTC)': 'BTC',
            'Ethereum (ETH)': 'ETH',
            'Cardano (ADA)': 'ADA',
            'Gold Bullion (1 oz)': 'XAU',
            'Silver Bullion (1 oz)': 'XAG',
            'Platinum Coins (1 oz)': 'XPT',
            'Luxury Apartment - Lagos': 'PROPERTY_FUND',
            'Downtown Apartment': 'PROPERTY_FUND',
            'Commercial Office Space': 'PROPERTY_FUND',
            'Real Estate Investment Trust': 'REIT_INDEX',
            'Bitcoin Investment Fund': 'BTC',
            'Silver Bars (10 oz)': 'XAG',
            'Platinum Bullion (1 oz)': 'XPT',
            'Commercial Property - Abuja': 'PROPERTY_FUND',
            'Commercial Property Fund': 'PROPERTY_FUND',
        }
        
        updated_count = 0
        for item_name, symbol in symbol_mappings.items():
            try:
                item = InvestmentItem.objects.filter(name=item_name, is_active=True).first()
                if item:
                    if not item.symbol:
                        item.symbol = symbol
                        item.save()
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Updated {item_name}: Added symbol {symbol}")
                        )
                        updated_count += 1
                    else:
                        self.stdout.write(f"ℹ️  {item_name}: Already has symbol {item.symbol}")
                else:
                    self.stdout.write(
                        self.style.WARNING(f"❌ Item not found: {item_name}")
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error updating {item_name}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"🎯 Updated {updated_count} items with symbols")
        )

    def verify_fixes(self):
        """Verify that all fixes are working"""
        # Check items
        items = InvestmentItem.objects.filter(is_active=True)
        self.stdout.write(f"📦 Active Investment Items: {items.count()}")
        
        # Check price feeds
        price_feeds = RealTimePriceFeed.objects.filter(is_active=True)
        self.stdout.write(f"💰 Active Price Feeds: {price_feeds.count()}")
        
        # Check items with symbols
        items_with_symbols = items.filter(symbol__isnull=False)
        self.stdout.write(f"🎯 Items with Live Price Symbols: {items_with_symbols.count()}")
        
        # Check price feed connections
        connected_items = 0
        for item in items_with_symbols:
            feed = RealTimePriceFeed.objects.filter(symbol=item.symbol, is_active=True).first()
            if feed:
                connected_items += 1
                self.stdout.write(f"  ✅ {item.name} -> {feed.name} (${feed.current_price})")
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ❌ {item.name} -> No active price feed for symbol '{item.symbol}'")
                )
        
        self.stdout.write(f"\n🎯 Total Connected Items: {connected_items}/{items_with_symbols.count()}")
        
        if connected_items == items_with_symbols.count():
            self.stdout.write(
                self.style.SUCCESS("🎉 All items with symbols are properly connected to price feeds!")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️  Some items are not properly connected to price feeds")
            )
