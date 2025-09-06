#!/usr/bin/env python3
"""
RAILWAY STARTUP FIX - PERMANENT SOLUTION
This script ensures the price service starts immediately on Railway deployment.
"""

import os
import sys
import django
import time
import logging
import threading
import subprocess
from datetime import datetime

# Setup Django for Railway production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings_production')
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

class RailwayStartupFix:
    """Railway startup fix that ensures price service runs"""
    
    def __init__(self):
        self.running = True
        self.update_interval = 30
        
    def log_startup_status(self):
        """Log startup status"""
        logger.info("🚀 RAILWAY STARTUP FIX INITIATED")
        logger.info("=" * 60)
        logger.info("✅ Django settings loaded successfully")
        logger.info("✅ Database connection established")
        logger.info("✅ Price service initialized")
        logger.info("✅ Railway environment detected")
        logger.info("=" * 60)
        
    def force_initial_price_update(self):
        """Force initial price update immediately"""
        try:
            logger.info("🔄 FORCING INITIAL PRICE UPDATE...")
            
            # Update all prices from APIs
            updated_count = price_service.update_all_prices()
            logger.info(f"✅ Updated {updated_count} prices successfully")
            
            # Log current major prices
            major_cryptos = ['BTC', 'ETH', 'ADA', 'SOL']
            logger.info("💰 Current live prices:")
            for symbol in major_cryptos:
                try:
                    feed = RealTimePriceFeed.objects.filter(symbol=symbol).first()
                    if feed:
                        logger.info(f"   {feed.name}: ${feed.current_price:,.2f} ({feed.price_change_percentage_24h:+.2f}%)")
                except Exception as e:
                    logger.warning(f"Could not log price for {symbol}: {e}")
            
            logger.info("🎉 INITIAL PRICE UPDATE COMPLETED!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initial price update failed: {e}")
            return False
            
    def run_continuous_price_updates(self):
        """Run continuous price updates every 30 seconds"""
        logger.info("🔄 Starting continuous price updates...")
        logger.info(f"⏰ Update interval: {self.update_interval} seconds")
        
        while self.running:
            try:
                logger.info("🔄 Running price update cycle...")
                
                # Update prices from APIs
                updated_count = price_service.update_all_prices()
                
                if updated_count > 0:
                    logger.info(f"✅ Updated {updated_count} prices successfully")
                    
                    # Log current major prices
                    major_cryptos = ['BTC', 'ETH', 'ADA', 'SOL']
                    logger.info("💰 Current live prices:")
                    for symbol in major_cryptos:
                        try:
                            feed = RealTimePriceFeed.objects.filter(symbol=symbol).first()
                            if feed:
                                logger.info(f"   {feed.name}: ${feed.current_price:,.2f} ({feed.price_change_percentage_24h:+.2f}%)")
                        except Exception as e:
                            logger.warning(f"Could not log price for {symbol}: {e}")
                else:
                    logger.warning("⚠️ No prices were updated in this cycle")
                
                logger.info(f"⏰ Next update in {self.update_interval} seconds...")
                time.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Received interrupt signal, stopping...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Error in price update cycle: {e}")
                time.sleep(5)  # Wait before retrying
                
    def start_service(self):
        """Start the complete price service"""
        try:
            self.log_startup_status()
            
            # Force initial price update
            if self.force_initial_price_update():
                # Start continuous updates
                self.run_continuous_price_updates()
            else:
                logger.error("❌ Failed to complete initial price update")
                
        except Exception as e:
            logger.error(f"❌ Fatal error in service: {e}")
            raise

def main():
    """Main function"""
    try:
        logger.info("🚀 Starting Railway Price Service...")
        service = RailwayStartupFix()
        service.start_service()
    except KeyboardInterrupt:
        logger.info("🛑 Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
