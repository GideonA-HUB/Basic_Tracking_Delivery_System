#!/usr/bin/env python3
"""
Start Real-Time Price System
This script starts the complete real-time price update system for production.
"""

import os
import sys
import django
import subprocess
import time
import signal
import logging
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings_production')
django.setup()

from django.utils import timezone
from investments.models import RealTimePriceFeed, InvestmentItem
from investments.tasks import update_real_time_prices

logger = logging.getLogger(__name__)

class RealTimePriceSystem:
    """Manages the real-time price update system"""
    
    def __init__(self):
        self.running = False
        self.update_interval = 30  # seconds
        self.last_update = None
        
    def start_system(self):
        """Start the real-time price system"""
        logger.info("🚀 Starting Real-Time Price System...")
        
        # Check if price feeds exist
        feeds_count = RealTimePriceFeed.objects.count()
        items_count = InvestmentItem.objects.count()
        
        logger.info(f"📊 Found {feeds_count} price feeds and {items_count} investment items")
        
        if feeds_count == 0:
            logger.warning("⚠️ No price feeds found. Creating default feeds...")
            self.create_default_price_feeds()
        
        self.running = True
        logger.info("✅ Real-Time Price System started successfully!")
        
        # Start continuous updates
        self.run_continuous_updates()
    
    def create_default_price_feeds(self):
        """Create default price feeds if none exist"""
        default_feeds = [
            {'symbol': 'BTC', 'name': 'Bitcoin', 'current_price': 111000.00},
            {'symbol': 'ETH', 'name': 'Ethereum', 'current_price': 4300.00},
            {'symbol': 'ADA', 'name': 'Cardano', 'current_price': 0.80},
            {'symbol': 'XAU', 'name': 'Gold (1 oz)', 'current_price': 2000.00},
            {'symbol': 'XAG', 'name': 'Silver (1 oz)', 'current_price': 25.00},
            {'symbol': 'XPT', 'name': 'Platinum (1 oz)', 'current_price': 1000.00},
        ]
        
        for feed_data in default_feeds:
            RealTimePriceFeed.objects.get_or_create(
                symbol=feed_data['symbol'],
                defaults={
                    'name': feed_data['name'],
                    'current_price': feed_data['current_price'],
                    'price_change_24h': 0,
                    'price_change_percentage_24h': 0,
                    'is_active': True,
                    'last_updated': timezone.now()
                }
            )
        
        logger.info(f"✅ Created {len(default_feeds)} default price feeds")
    
    def run_continuous_updates(self):
        """Run continuous price updates"""
        logger.info(f"🔄 Starting continuous updates every {self.update_interval} seconds...")
        
        try:
            while self.running:
                try:
                    # Run price update task
                    logger.info("📈 Running price update...")
                    result = update_real_time_prices.delay()
                    
                    # Wait for result (with timeout)
                    try:
                        update_result = result.get(timeout=60)
                        logger.info(f"✅ Price update completed: {update_result} items updated")
                    except Exception as e:
                        logger.error(f"❌ Price update failed: {e}")
                    
                    self.last_update = timezone.now()
                    
                    # Wait for next update
                    time.sleep(self.update_interval)
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Received interrupt signal, stopping...")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in update cycle: {e}")
                    time.sleep(10)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"❌ Fatal error in continuous updates: {e}")
        finally:
            self.stop_system()
    
    def stop_system(self):
        """Stop the real-time price system"""
        logger.info("🛑 Stopping Real-Time Price System...")
        self.running = False
        logger.info("✅ Real-Time Price System stopped")
    
    def get_status(self):
        """Get system status"""
        return {
            'running': self.running,
            'last_update': self.last_update,
            'update_interval': self.update_interval,
            'feeds_count': RealTimePriceFeed.objects.count(),
            'items_count': InvestmentItem.objects.count()
        }

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    logger.info(f"🛑 Received signal {signum}, stopping system...")
    if 'system' in globals():
        system.stop_system()
    sys.exit(0)

def main():
    """Main function"""
    print("🚀 Real-Time Price System Starter")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('real_time_price_system.log')
        ]
    )
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start system
    global system
    system = RealTimePriceSystem()
    
    try:
        system.start_system()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
