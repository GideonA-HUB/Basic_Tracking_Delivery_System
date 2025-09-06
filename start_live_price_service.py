#!/usr/bin/env python3
"""
Start Live Price Service
This script starts the live price update service to fetch real prices from APIs
and update the database continuously.
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

from django.utils import timezone
from investments.price_services import price_service
from investments.models import RealTimePriceFeed, InvestmentItem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LivePriceService:
    """Live price service that runs continuously"""
    
    def __init__(self):
        self.running = False
        self.update_interval = 30  # Update every 30 seconds
        self.last_update = None
        
    def start(self):
        """Start the live price service"""
        logger.info("🚀 Starting Live Price Service...")
        
        # Check current state
        feeds_count = RealTimePriceFeed.objects.filter(is_active=True).count()
        items_count = InvestmentItem.objects.filter(is_active=True).count()
        
        logger.info(f"📊 Found {feeds_count} active price feeds and {items_count} investment items")
        
        self.running = True
        logger.info("✅ Live Price Service started successfully!")
        logger.info(f"📡 Fetching real prices every {self.update_interval} seconds")
        
        # Start continuous updates
        self.run_continuous_updates()
    
    def run_continuous_updates(self):
        """Run continuous price updates"""
        try:
            while self.running:
                try:
                    logger.info("🔄 Starting price update cycle...")
                    
                    # Update all prices
                    updated_count = price_service.update_all_prices()
                    
                    if updated_count > 0:
                        logger.info(f"✅ Updated {updated_count} prices successfully")
                        
                        # Show some current prices
                        self.show_current_prices()
                    else:
                        logger.warning("⚠️ No prices were updated")
                    
                    self.last_update = timezone.now()
                    logger.info(f"⏰ Next update in {self.update_interval} seconds...")
                    
                except Exception as e:
                    logger.error(f"❌ Error in price update cycle: {e}")
                
                # Wait before next update
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Stopping Live Price Service...")
            self.running = False
    
    def show_current_prices(self):
        """Show current prices for major cryptocurrencies"""
        try:
            major_coins = ['BTC', 'ETH', 'ADA', 'SOL']
            feeds = RealTimePriceFeed.objects.filter(symbol__in=major_coins, is_active=True)
            
            logger.info("💰 Current major cryptocurrency prices:")
            for feed in feeds:
                logger.info(f"   {feed.name}: ${feed.current_price:,.2f}")
                
        except Exception as e:
            logger.error(f"Error showing current prices: {e}")
    
    def stop(self):
        """Stop the live price service"""
        self.running = False
        logger.info("✅ Live Price Service stopped")

def main():
    """Main function to start the service"""
    try:
        logger.info("🎯 Starting Live Price Service...")
        
        # Create and start the service
        service = LivePriceService()
        
        # Run initial update
        logger.info("🔄 Running initial price update...")
        updated_count = price_service.update_all_prices()
        logger.info(f"✅ Initial update completed: {updated_count} prices updated")
        
        # Start continuous updates
        service.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down service...")
        service.stop()
    except Exception as e:
        logger.error(f"❌ Failed to start service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()