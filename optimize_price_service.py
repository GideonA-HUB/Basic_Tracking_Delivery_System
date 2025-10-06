#!/usr/bin/env python
"""
Price Service Optimization Script
Fixes rate limiting issues and optimizes API calls
"""
import os
import sys
import django
import time
import logging
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.price_services import RealTimePriceService
from investments.models import RealTimePriceFeed
from django.utils import timezone

logger = logging.getLogger(__name__)

class PriceServiceOptimizer:
    """Optimizes price service to avoid rate limiting"""
    
    def __init__(self):
        self.price_service = RealTimePriceService()
        self.api_call_times = {}
        self.min_interval = 300  # 5 minutes between calls to same API
        
    def can_make_api_call(self, api_name):
        """Check if enough time has passed since last API call"""
        if api_name not in self.api_call_times:
            return True
        
        last_call = self.api_call_times[api_name]
        time_since_last = (timezone.now() - last_call).total_seconds()
        
        return time_since_last >= self.min_interval
    
    def record_api_call(self, api_name):
        """Record the time of API call"""
        self.api_call_times[api_name] = timezone.now()
    
    def optimize_price_update(self):
        """Optimize price updates with rate limiting"""
        logger.info("🔄 Starting optimized price update...")
        
        total_updated = 0
        
        # Update crypto prices (if enough time has passed)
        if self.can_make_api_call('crypto'):
            try:
                logger.info("📡 Fetching crypto prices...")
                crypto_prices = self.price_service.fetch_crypto_prices()
                if crypto_prices:
                    updated = self.update_crypto_prices(crypto_prices)
                    total_updated += updated
                    self.record_api_call('crypto')
                    logger.info(f"✅ Updated {updated} crypto prices")
                else:
                    logger.warning("⚠️ No crypto prices received")
            except Exception as e:
                logger.error(f"❌ Error fetching crypto prices: {e}")
        else:
            logger.info("⏰ Skipping crypto prices (rate limit)")
        
        # Update metals prices (if enough time has passed)
        if self.can_make_api_call('metals'):
            try:
                logger.info("📡 Fetching metals prices...")
                metals_prices = self.price_service.fetch_gold_silver_prices()
                if metals_prices:
                    updated = self.update_metals_prices(metals_prices)
                    total_updated += updated
                    self.record_api_call('metals')
                    logger.info(f"✅ Updated {updated} metals prices")
                else:
                    logger.warning("⚠️ No metals prices received")
            except Exception as e:
                logger.error(f"❌ Error fetching metals prices: {e}")
        else:
            logger.info("⏰ Skipping metals prices (rate limit)")
        
        # Update real estate prices (if enough time has passed)
        if self.can_make_api_call('real_estate'):
            try:
                logger.info("📡 Fetching real estate prices...")
                real_estate_prices = self.price_service.fetch_real_estate_prices()
                if real_estate_prices:
                    updated = self.update_real_estate_prices(real_estate_prices)
                    total_updated += updated
                    self.record_api_call('real_estate')
                    logger.info(f"✅ Updated {updated} real estate prices")
                else:
                    logger.warning("⚠️ No real estate prices received")
            except Exception as e:
                logger.error(f"❌ Error fetching real estate prices: {e}")
        else:
            logger.info("⏰ Skipping real estate prices (rate limit)")
        
        logger.info(f"🎉 Total prices updated: {total_updated}")
        return total_updated
    
    def update_crypto_prices(self, prices):
        """Update crypto prices in database"""
        updated_count = 0
        
        for symbol, price_data in prices.items():
            try:
                feed, created = RealTimePriceFeed.objects.get_or_create(
                    symbol=symbol,
                    defaults={
                        'name': f"{symbol} Price Feed",
                        'current_price': price_data['price'],
                        'price_change_24h': price_data['change_24h'],
                        'price_change_percentage_24h': (
                            (price_data['change_24h'] / price_data['price'] * 100) 
                            if price_data['price'] > 0 else 0
                        ),
                        'volume_24h': price_data.get('volume_24h', 0),
                        'market_cap': price_data.get('market_cap', 0),
                        'last_updated': timezone.now(),
                        'is_active': True
                    }
                )
                
                if not created:
                    # Update existing feed
                    feed.current_price = price_data['price']
                    feed.price_change_24h = price_data['change_24h']
                    feed.price_change_percentage_24h = (
                        (price_data['change_24h'] / price_data['price'] * 100) 
                        if price_data['price'] > 0 else 0
                    )
                    feed.volume_24h = price_data.get('volume_24h', 0)
                    feed.market_cap = price_data.get('market_cap', 0)
                    feed.last_updated = timezone.now()
                    feed.save()
                
                updated_count += 1
                logger.info(f"   {symbol}: ${price_data['price']} ({feed.price_change_percentage_24h:+.2f}%)")
                
            except Exception as e:
                logger.error(f"   ❌ Error updating {symbol}: {e}")
        
        return updated_count
    
    def update_metals_prices(self, prices):
        """Update metals prices in database"""
        updated_count = 0
        metal_names = {
            'XAU': 'Gold',
            'XAG': 'Silver', 
            'XPT': 'Platinum'
        }
        
        for symbol, price_data in prices.items():
            try:
                name = metal_names.get(symbol, symbol)
                feed, created = RealTimePriceFeed.objects.get_or_create(
                    symbol=symbol,
                    defaults={
                        'name': f"{name} ({symbol})",
                        'current_price': price_data['price'],
                        'price_change_24h': price_data.get('change_24h', 0),
                        'price_change_percentage_24h': (
                            (price_data.get('change_24h', 0) / price_data['price'] * 100) 
                            if price_data['price'] > 0 else 0
                        ),
                        'volume_24h': price_data.get('volume_24h', 0),
                        'market_cap': price_data.get('market_cap', 0),
                        'last_updated': timezone.now(),
                        'is_active': True
                    }
                )
                
                if not created:
                    feed.current_price = price_data['price']
                    feed.price_change_24h = price_data.get('change_24h', 0)
                    feed.price_change_percentage_24h = (
                        (price_data.get('change_24h', 0) / price_data['price'] * 100) 
                        if price_data['price'] > 0 else 0
                    )
                    feed.volume_24h = price_data.get('volume_24h', 0)
                    feed.market_cap = price_data.get('market_cap', 0)
                    feed.last_updated = timezone.now()
                    feed.save()
                
                updated_count += 1
                logger.info(f"   {name} ({symbol}): ${price_data['price']}")
                
            except Exception as e:
                logger.error(f"   ❌ Error updating {symbol}: {e}")
        
        return updated_count
    
    def update_real_estate_prices(self, prices):
        """Update real estate prices in database"""
        updated_count = 0
        
        for symbol, price_data in prices.items():
            try:
                feed, created = RealTimePriceFeed.objects.get_or_create(
                    symbol=symbol,
                    defaults={
                        'name': f"{symbol} Real Estate",
                        'current_price': price_data['price'],
                        'price_change_24h': price_data.get('change_24h', 0),
                        'price_change_percentage_24h': (
                            (price_data.get('change_24h', 0) / price_data['price'] * 100) 
                            if price_data['price'] > 0 else 0
                        ),
                        'volume_24h': price_data.get('volume_24h', 0),
                        'market_cap': price_data.get('market_cap', 0),
                        'last_updated': timezone.now(),
                        'is_active': True
                    }
                )
                
                if not created:
                    feed.current_price = price_data['price']
                    feed.price_change_24h = price_data.get('change_24h', 0)
                    feed.price_change_percentage_24h = (
                        (price_data.get('change_24h', 0) / price_data['price'] * 100) 
                        if price_data['price'] > 0 else 0
                    )
                    feed.volume_24h = price_data.get('volume_24h', 0)
                    feed.market_cap = price_data.get('market_cap', 0)
                    feed.last_updated = timezone.now()
                    feed.save()
                
                updated_count += 1
                logger.info(f"   {symbol} Real Estate: ${price_data['price']}")
                
            except Exception as e:
                logger.error(f"   ❌ Error updating {symbol}: {e}")
        
        return updated_count

def main():
    """Main function to run price optimization"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    optimizer = PriceServiceOptimizer()
    
    try:
        logger.info("🚀 Starting Price Service Optimization")
        logger.info("=" * 50)
        
        # Run optimized price update
        total_updated = optimizer.optimize_price_update()
        
        logger.info("=" * 50)
        logger.info(f"✅ Optimization completed. Updated {total_updated} prices.")
        
        # Show current prices
        logger.info("💰 Current prices in database:")
        feeds = RealTimePriceFeed.objects.filter(is_active=True)
        for feed in feeds:
            logger.info(f"   {feed.name}: ${feed.current_price:,.2f} ({feed.price_change_percentage_24h:+.2f}%)")
        
    except Exception as e:
        logger.error(f"❌ Error in optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
