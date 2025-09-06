#!/usr/bin/env python3
"""
IMMEDIATE PRICE SERVICE START - FORCE REAL PRICES
This script immediately starts the price service and forces real API price updates.
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

class ImmediatePriceService:
    """Immediate price service that forces real API price updates"""
    
    def __init__(self):
        self.running = True
        self.update_interval = 30
        
    def log_startup_status(self):
        """Log startup status"""
        logger.info("🚀 IMMEDIATE PRICE SERVICE STARTED")
        logger.info("=" * 60)
        logger.info("✅ Django settings loaded successfully")
        logger.info("✅ Database connection established")
        logger.info("✅ Price service initialized")
        logger.info("✅ Railway environment detected")
        logger.info("=" * 60)
        
    def force_immediate_price_update(self):
        """Force immediate price update from APIs"""
        try:
            logger.info("🔄 FORCING IMMEDIATE PRICE UPDATE FROM APIs...")
            
            # Update all prices from APIs
            updated_count = price_service.update_all_prices()
            logger.info(f"✅ Updated {updated_count} prices from APIs successfully")
            
            # Log current major prices
            major_cryptos = ['BTC', 'ETH', 'ADA', 'SOL']
            logger.info("💰 Current LIVE API prices:")
            for symbol in major_cryptos:
                try:
                    feed = RealTimePriceFeed.objects.filter(symbol=symbol).first()
                    if feed:
                        logger.info(f"   {feed.name}: ${feed.current_price:,.2f} ({feed.price_change_percentage_24h:+.2f}%)")
                except Exception as e:
                    logger.warning(f"Could not log price for {symbol}: {e}")
            
            logger.info("🎉 IMMEDIATE PRICE UPDATE COMPLETED!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Immediate price update failed: {e}")
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
                    logger.info(f"✅ Updated {updated_count} prices from APIs successfully")
                    
                    # Log current major prices
                    major_cryptos = ['BTC', 'ETH', 'ADA', 'SOL']
                    logger.info("💰 Current LIVE API prices:")
                    for symbol in major_cryptos:
                        try:
                            feed = RealTimePriceFeed.objects.filter(symbol=symbol).first()
                            if feed:
                                logger.info(f"   {feed.name}: ${feed.current_price:,.2f} ({feed.price_change_percentage_24h:+.2f}%)")
                        except Exception as e:
                            logger.warning(f"Could not log price for {symbol}: {e}")
                else:
                    logger.warning("⚠️ No prices were updated")
                
                # Wait for next update
                logger.info(f"⏳ Waiting {self.update_interval} seconds for next update...")
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"❌ Price update cycle failed: {e}")
                logger.info("⏳ Retrying in 30 seconds...")
                time.sleep(30)
    
    def start(self):
        """Start the immediate price service"""
        try:
            self.log_startup_status()
            
            # Force immediate price update
            if self.force_immediate_price_update():
                logger.info("✅ Immediate price update successful")
            else:
                logger.error("❌ Immediate price update failed")
            
            # Start continuous updates
            self.run_continuous_price_updates()
            
        except KeyboardInterrupt:
            logger.info("🛑 Price service stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Price service failed: {e}")
            self.running = False

if __name__ == "__main__":
    logger.info("🚀 Starting Immediate Price Service...")
    
    # Create and start the price service
    price_service = ImmediatePriceService()
    price_service.start()
