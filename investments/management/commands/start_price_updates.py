from django.core.management.base import BaseCommand
from django.utils import timezone
from investments.models import InvestmentItem, RealTimePriceFeed, PriceMovementStats
from investments.price_services import price_service
from investments.tasks import update_real_time_prices, update_investment_item_prices
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start the real-time price update system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Run a test price update',
        )
        parser.add_argument(
            '--setup-feeds',
            action='store_true',
            help='Setup initial price feeds',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting Real-Time Price Update System'))
        
        if options['setup_feeds']:
            self.setup_price_feeds()
        
        if options['test']:
            self.run_test_update()
        else:
            self.start_continuous_updates()
    
    def setup_price_feeds(self):
        """Setup initial price feeds for all investment items"""
        self.stdout.write('📊 Setting up price feeds...')
        
        # Create price feeds for common assets
        price_feeds_data = [
            {'symbol': 'BTC', 'name': 'Bitcoin (BTC)', 'current_price': 45000.00},
            {'symbol': 'ETH', 'name': 'Ethereum (ETH)', 'current_price': 3000.00},
            {'symbol': 'ADA', 'name': 'Cardano (ADA)', 'current_price': 0.50},
            {'symbol': 'XAU', 'name': 'Gold Bullion (1 oz)', 'current_price': 2000.00},
            {'symbol': 'XAG', 'name': 'Silver Bullion (1 oz)', 'current_price': 25.00},
            {'symbol': 'XPT', 'name': 'Platinum Bullion (1 oz)', 'current_price': 1000.00},
        ]
        
        created_count = 0
        for feed_data in price_feeds_data:
            feed, created = RealTimePriceFeed.objects.get_or_create(
                symbol=feed_data['symbol'],
                defaults={
                    'name': feed_data['name'],
                    'current_price': feed_data['current_price'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"✅ Created price feed for {feed_data['name']}")
        
        self.stdout.write(self.style.SUCCESS(f'📈 Created {created_count} new price feeds'))
    
    def run_test_update(self):
        """Run a test price update"""
        self.stdout.write('🧪 Running test price update...')
        
        try:
            # Update prices using the price service
            updated_count = price_service.update_all_prices()
            
            if updated_count > 0:
                self.stdout.write(self.style.SUCCESS(f'✅ Updated {updated_count} prices successfully'))
                
                # Show some updated prices
                feeds = RealTimePriceFeed.objects.filter(is_active=True)[:5]
                for feed in feeds:
                    self.stdout.write(f"   {feed.name}: ${feed.current_price} ({feed.price_change_percentage_24h:+.2f}%)")
            else:
                self.stdout.write(self.style.WARNING('⚠️  No prices were updated'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error during test update: {e}'))
            logger.error(f"Error during test update: {e}")
    
    def start_continuous_updates(self):
        """Start continuous price updates"""
        self.stdout.write('🔄 Starting continuous price updates...')
        self.stdout.write('Press Ctrl+C to stop')
        
        try:
            import time
            while True:
                try:
                    # Run price update
                    updated_count = price_service.update_all_prices()
                    
                    if updated_count > 0:
                        self.stdout.write(f'📈 Updated {updated_count} prices at {timezone.now().strftime("%H:%M:%S")}')
                    else:
                        self.stdout.write(f'⏳ No price updates at {timezone.now().strftime("%H:%M:%S")}')
                    
                    # Wait 5 minutes before next update
                    time.sleep(300)
                    
                except KeyboardInterrupt:
                    self.stdout.write(self.style.SUCCESS('\n🛑 Stopping price updates...'))
                    break
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error during update: {e}'))
                    logger.error(f"Error during continuous update: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
                    
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\n✅ Price update system stopped'))
    
    def show_status(self):
        """Show current system status"""
        self.stdout.write('\n📊 System Status:')
        
        # Count active items
        active_items = InvestmentItem.objects.filter(is_active=True).count()
        featured_items = InvestmentItem.objects.filter(is_active=True, is_featured=True).count()
        active_feeds = RealTimePriceFeed.objects.filter(is_active=True).count()
        
        self.stdout.write(f'   Active investment items: {active_items}')
        self.stdout.write(f'   Featured items: {featured_items}')
        self.stdout.write(f'   Active price feeds: {active_feeds}')
        
        # Show recent price movements
        recent_movements = PriceMovementStats.objects.filter(
            date=timezone.now().date()
        ).aggregate(
            total_increases=models.Sum('increases_today'),
            total_decreases=models.Sum('decreases_today')
        )
        
        increases = recent_movements['total_increases'] or 0
        decreases = recent_movements['total_decreases'] or 0
        
        self.stdout.write(f'   Price increases today: {increases}')
        self.stdout.write(f'   Price decreases today: {decreases}')
