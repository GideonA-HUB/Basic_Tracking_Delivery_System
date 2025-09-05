from django.core.management.base import BaseCommand
from django.utils import timezone
import time
import logging
from investments.tasks import update_real_time_prices, update_investment_item_prices
from investments.price_services import price_service

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Start live price updates without Celery'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Update interval in seconds (default: 60)'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once and exit'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        run_once = options['once']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Starting live price updates (interval: {interval}s)')
        )
        
        if run_once:
            self.stdout.write('🔄 Running price update once...')
            self.run_price_update()
            self.stdout.write(self.style.SUCCESS('✅ Price update completed'))
            return
        
        self.stdout.write('🔄 Starting continuous price updates...')
        self.stdout.write('Press Ctrl+C to stop')
        
        try:
            while True:
                self.run_price_update()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n⏹️  Price updates stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error in price updates: {e}')
            )
    
    def run_price_update(self):
        """Run a single price update cycle"""
        try:
            # Update price feeds
            updated_count = price_service.update_all_prices()
            
            # Update investment item prices
            price_service.update_investment_item_prices()
            
            timestamp = timezone.now().strftime('%H:%M:%S')
            self.stdout.write(f'[{timestamp}] ✅ Updated {updated_count} prices')
            
        except Exception as e:
            timestamp = timezone.now().strftime('%H:%M:%S')
            self.stdout.write(
                self.style.ERROR(f'[{timestamp}] ❌ Error: {e}')
            )
