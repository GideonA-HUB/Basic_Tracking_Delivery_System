#!/usr/bin/env python
"""
Background Price Worker for Railway
Continuously fetches prices from APIs and updates database
"""
import os
import sys
import django
import asyncio
import logging
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.price_services import RealTimePriceService
from investments.models import RealTimePriceFeed
from django.utils import timezone

logger = logging.getLogger(__name__)

class BackgroundPriceWorker:
    """Background worker for continuous price updates"""
    
    def __init__(self):
        self.price_service = RealTimePriceService()
        self.running = True
        self.update_interval = 300  # 5 minutes
        self.last_update = None
        
    async def start(self):
        """Start the background price worker"""
        logger.info("🚀 Starting Background Price Worker")
        logger.info(f"Update interval: {self.update_interval} seconds")
        
        while self.running:
            try:
                logger.info("🔄 Starting price update cycle...")
                await self.update_all_prices()
                
                # Wait for next update
                logger.info(f"⏰ Waiting {self.update_interval} seconds until next update...")
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in background worker: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(60)
    
    async def update_all_prices(self):
        """Update all prices from APIs"""
        try:
            # Fetch crypto prices
            crypto_prices = await self.fetch_crypto_prices_async()
            if crypto_prices:
                await self.update_crypto_prices(crypto_prices)
            
            # Fetch metals prices
            metals_prices = await self.fetch_metals_prices_async()
            if metals_prices:
                await self.update_metals_prices(metals_prices)
            
            # Fetch real estate prices (static for now)
            real_estate_prices = await self.fetch_real_estate_prices_async()
            if real_estate_prices:
                await self.update_real_estate_prices(real_estate_prices)
            
            self.last_update = timezone.now()
            logger.info(f"✅ Price update completed at {self.last_update}")
            
        except Exception as e:
            logger.error(f"❌ Error updating prices: {e}")
    
    async def fetch_crypto_prices_async(self):
        """Fetch crypto prices asynchronously"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.price_service.fetch_crypto_prices)
    
    async def fetch_metals_prices_async(self):
        """Fetch metals prices asynchronously"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.price_service.fetch_gold_silver_prices)
    
    async def fetch_real_estate_prices_async(self):
        """Fetch real estate prices asynchronously"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.price_service.fetch_real_estate_prices)
    
    async def update_crypto_prices(self, prices):
        """Update crypto prices in database"""
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
                
                logger.info(f"✅ Updated {symbol}: ${price_data['price']} ({feed.price_change_percentage_24h:+.2f}%)")
                
            except Exception as e:
                logger.error(f"❌ Error updating {symbol}: {e}")
    
    async def update_metals_prices(self, prices):
        """Update metals prices in database"""
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
                
                logger.info(f"✅ Updated {name} ({symbol}): ${price_data['price']}")
                
            except Exception as e:
                logger.error(f"❌ Error updating {symbol}: {e}")
    
    async def update_real_estate_prices(self, prices):
        """Update real estate prices in database"""
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
                
                logger.info(f"✅ Updated {symbol} Real Estate: ${price_data['price']}")
                
            except Exception as e:
                logger.error(f"❌ Error updating {symbol}: {e}")
    
    def stop(self):
        """Stop the background worker"""
        self.running = False
        logger.info("🛑 Background Price Worker stopped")

async def main():
    """Main function to run the background worker"""
    worker = BackgroundPriceWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
        worker.stop()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        worker.stop()

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the worker
    asyncio.run(main())
