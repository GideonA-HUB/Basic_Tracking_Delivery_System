#!/usr/bin/env python
"""
Start the real-time price service for the investment system
This script runs the price update tasks and WebSocket server
"""
import os
import sys
import django
import time
import logging
import threading
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.tasks import update_real_time_prices, update_investment_item_prices
from investments.price_services import price_service
from django.utils import timezone

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_time_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealTimePriceService:
    """Real-time price service that runs continuously"""
    
    def __init__(self):
        self.running = False
        self.update_interval = 60  # Update every 60 seconds
        self.last_update = None
        
    def start(self):
        """Start the real-time price service"""
        logger.info("🚀 Starting Real-Time Price Service...")
        self.running = True
        
        # Start price update thread
        price_thread = threading.Thread(target=self.price_update_loop, daemon=True)
        price_thread.start()
        
        # Start investment item update thread
        item_thread = threading.Thread(target=self.investment_item_update_loop, daemon=True)
        item_thread.start()
        
        logger.info("✅ Real-Time Price Service started successfully!")
        logger.info(f"📊 Price updates every {self.update_interval} seconds")
        logger.info("🔄 Investment item updates every 2 minutes")
        logger.info("🌐 WebSocket server ready for real-time connections")
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down Real-Time Price Service...")
            self.stop()
    
    def stop(self):
        """Stop the real-time price service"""
        self.running = False
        logger.info("✅ Real-Time Price Service stopped")
    
    def price_update_loop(self):
        """Main price update loop"""
        while self.running:
            try:
                logger.info("🔄 Updating real-time prices...")
                
                # Update all prices
                updated_count = price_service.update_all_prices()
                
                if updated_count > 0:
                    logger.info(f"✅ Updated {updated_count} price feeds")
                    
                    # Try to run Celery tasks if available
                    try:
                        update_real_time_prices.delay()
                        logger.info("📤 Sent price update task to Celery")
                    except Exception as e:
                        logger.warning(f"⚠️ Celery task failed: {e}")
                else:
                    logger.warning("⚠️ No prices were updated")
                
                self.last_update = timezone.now()
                
            except Exception as e:
                logger.error(f"❌ Error updating prices: {e}")
            
            # Wait for next update
            time.sleep(self.update_interval)
    
    def investment_item_update_loop(self):
        """Investment item price update loop"""
        while self.running:
            try:
                logger.info("🔄 Updating investment item prices...")
                
                # Update investment item prices
                from investments.models import InvestmentItem, RealTimePriceFeed
                
                updated_count = 0
                items = InvestmentItem.objects.filter(is_active=True)
                
                for item in items:
                    if item.symbol:
                        feed = RealTimePriceFeed.objects.filter(symbol=item.symbol, is_active=True).first()
                        if feed and feed.current_price != item.current_price_usd:
                            old_price = item.current_price_usd
                            new_price = feed.current_price
                            
                            # Calculate price change
                            price_change = new_price - old_price
                            price_change_percentage = (price_change / old_price * 100) if old_price > 0 else 0
                            
                            # Update item price
                            item.update_price(
                                new_price,
                                price_change,
                                price_change_percentage,
                                volume_24h=feed.volume_24h if hasattr(feed, 'volume_24h') else None,
                                market_cap=feed.market_cap if hasattr(feed, 'market_cap') else None
                            )
                            
                            updated_count += 1
                            logger.info(f"📈 Updated {item.name}: ${new_price} ({price_change_percentage:+.2f}%)")
                
                if updated_count > 0:
                    logger.info(f"✅ Updated {updated_count} investment items")
                else:
                    logger.info("ℹ️ No investment items needed updates")
                
            except Exception as e:
                logger.error(f"❌ Error updating investment items: {e}")
            
            # Wait 2 minutes before next update
            time.sleep(120)
    
    def get_status(self):
        """Get service status"""
        return {
            'running': self.running,
            'last_update': self.last_update,
            'update_interval': self.update_interval
        }

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 MERIDIAN ASSET LOGISTICS - REAL-TIME PRICE SERVICE")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌐 Website: https://meridianassetlogistics.com")
    print("📊 Features:")
    print("   • Real-time cryptocurrency prices")
    print("   • Live precious metals prices")
    print("   • Real estate indices")
    print("   • WebSocket live updates")
    print("   • Investment portfolio tracking")
    print("=" * 60)
    
    # Create and start service
    service = RealTimePriceService()
    
    try:
        service.start()
    except KeyboardInterrupt:
        print("\n🛑 Service interrupted by user")
    except Exception as e:
        logger.error(f"❌ Service error: {e}")
    finally:
        service.stop()
        print("✅ Service stopped")

if __name__ == "__main__":
    main()
