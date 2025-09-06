"""
Django management command to update prices from APIs
"""

from django.core.management.base import BaseCommand
from investments.price_services import price_service
from investments.models import RealTimePriceFeed
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update prices from APIs'

    def handle(self, *args, **options):
        try:
            self.stdout.write("🔄 Updating prices from APIs...")
            
            # Update all prices from APIs
            updated_count = price_service.update_all_prices()
            
            if updated_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Updated {updated_count} prices successfully")
                )
                
                # Log current major prices
                major_cryptos = ['BTC', 'ETH', 'ADA', 'SOL']
                self.stdout.write("💰 Current LIVE API prices:")
                for symbol in major_cryptos:
                    try:
                        feed = RealTimePriceFeed.objects.filter(symbol=symbol).first()
                        if feed:
                            self.stdout.write(f"   {feed.name}: ${feed.current_price:,.2f} ({feed.price_change_percentage_24h:+.2f}%)")
                    except Exception as e:
                        self.stdout.write(f"   Could not log price for {symbol}: {e}")
            else:
                self.stdout.write(
                    self.style.WARNING("⚠️ No prices were updated")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Price update failed: {e}")
            )
