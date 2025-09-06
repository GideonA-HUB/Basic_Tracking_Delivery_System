#!/usr/bin/env python3
"""
RAILWAY EMERGENCY FIX
This script forces Railway to start the price service immediately.
"""

import os
import sys
import django
import time
import logging
import threading
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

def emergency_price_update():
    """Emergency price update for Railway production"""
    try:
        logger.info("🚨 RAILWAY EMERGENCY FIX STARTED")
        logger.info("=" * 50)
        
        # Force update all prices immediately
        logger.info("🔄 Force updating all prices from APIs...")
        updated_count = price_service.update_all_prices()
        logger.info(f"✅ Updated {updated_count} prices successfully")
        
        # Log current prices
        major_cryptos = ['BTC', 'ETH', 'ADA', 'SOL']
        logger.info("💰 Current live prices:")
        for symbol in major_cryptos:
            try:
                feed = RealTimePriceFeed.objects.filter(symbol=symbol).first()
                if feed:
                    logger.info(f"   {feed.name}: ${feed.current_price:,.2f} ({feed.price_change_percentage_24h:+.2f}%)")
            except Exception as e:
                logger.warning(f"Could not log price for {symbol}: {e}")
        
        logger.info("🎉 EMERGENCY FIX COMPLETED - Prices updated on Railway!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Emergency fix failed: {e}")
        return False

def run_continuous_updates():
    """Run continuous price updates every 30 seconds"""
    logger.info("🚀 Starting continuous price updates on Railway...")
    
    while True:
        try:
            emergency_price_update()
            logger.info("⏰ Waiting 30 seconds for next update...")
            time.sleep(30)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping price service...")
            break
        except Exception as e:
            logger.error(f"❌ Error in continuous updates: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        # Run emergency fix immediately
        if emergency_price_update():
            # Then run continuous updates
            run_continuous_updates()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
