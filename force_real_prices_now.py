#!/usr/bin/env python3
"""
FORCE REAL PRICES NOW - IMMEDIATE FIX
This script immediately fetches real prices from APIs and updates the database.
"""

import os
import sys
import django
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.price_services import price_service
from investments.models import RealTimePriceFeed, InvestmentItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_real_prices():
    """Force fetch real prices from APIs"""
    try:
        logger.info("🚀 FORCING REAL PRICE UPDATE FROM APIs...")
        
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
        
        logger.info("🎉 REAL PRICE UPDATE COMPLETED!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Real price update failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting Real Price Update...")
    force_real_prices()
