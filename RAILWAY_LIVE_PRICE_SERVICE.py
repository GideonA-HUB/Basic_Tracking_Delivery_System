#!/usr/bin/env python3
"""
RAILWAY LIVE PRICE SERVICE
==========================
A comprehensive live price fetching service designed specifically for Railway deployment.
This service will fetch real prices from multiple APIs and update the database continuously.

Features:
- Fetches real prices from CoinGecko, CoinPaprika, and other APIs
- Updates database with live prices
- Broadcasts updates via WebSocket
- Handles API failures gracefully
- Runs continuously in background
- Railway-optimized with proper error handling
"""

import os
import sys
import django
import time
import requests
import json
import logging
from datetime import datetime, timezone
from threading import Thread
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings_production')
django.setup()

# Import Django models after setup
from investments.models import (
    RealTimePriceFeed, InvestmentItem, PriceHistory, 
    RealTimePriceHistory, PriceMovementStats
)
from django.utils import timezone
from django.db import transaction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RailwayLivePriceService:
    """Railway-optimized live price service"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.api_errors = {}
        self.update_count = 0
        self.running = True
        
        # API endpoints with fallbacks
        self.crypto_apis = [
            {
                'name': 'CoinGecko',
                'url': 'https://api.coingecko.com/api/v3/simple/price',
                'params': {
                    'ids': 'bitcoin,ethereum,cardano,chainlink',
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true'
                }
            },
            {
                'name': 'CoinPaprika',
                'url': 'https://api.coinpaprika.com/v1/tickers',
                'params': {}
            }
        ]
        
        self.metal_apis = [
            {
                'name': 'MetalsAPI',
                'url': 'https://metals-api.com/api/latest',
                'params': {
                    'access_key': 'your_metals_api_key',  # Replace with actual key
                    'base': 'USD',
                    'symbols': 'XAU,XAG,XPT'
                }
            }
        ]
        
        # Default prices if APIs fail
        self.default_prices = {
            'BTC': 45000.0,
            'ETH': 3000.0,
            'ADA': 0.5,
            'LINK': 15.0,
            'GOLD': 2000.0,
            'SILVER': 25.0,
            'PLATINUM': 1000.0
        }
        
        logger.info("🚀 Railway Live Price Service initialized")
    
    def fetch_crypto_prices(self):
        """Fetch crypto prices from multiple APIs"""
        prices = {}
        
        for api in self.crypto_apis:
            try:
                logger.info(f"📡 Fetching from {api['name']}...")
                response = requests.get(api['url'], params=api['params'], timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if api['name'] == 'CoinGecko':
                    # Parse CoinGecko response
                    for coin_id, coin_data in data.items():
                        if coin_id == 'bitcoin':
                            prices['BTC'] = coin_data['usd']
                        elif coin_id == 'ethereum':
                            prices['ETH'] = coin_data['usd']
                        elif coin_id == 'cardano':
                            prices['ADA'] = coin_data['usd']
                        elif coin_id == 'chainlink':
                            prices['LINK'] = coin_data['usd']
                
                elif api['name'] == 'CoinPaprika':
                    # Parse CoinPaprika response
                    for ticker in data:
                        symbol = ticker['symbol']
                        if symbol in ['BTC', 'ETH', 'ADA', 'LINK']:
                            prices[symbol] = ticker['quotes']['USD']['price']
                
                logger.info(f"✅ Successfully fetched from {api['name']}")
                break  # Use first successful API
                
            except Exception as e:
                logger.warning(f"❌ Failed to fetch from {api['name']}: {e}")
                self.api_errors[api['name']] = str(e)
                continue
        
        # Use default prices for missing data
        for symbol, default_price in self.default_prices.items():
            if symbol in ['BTC', 'ETH', 'ADA', 'LINK'] and symbol not in prices:
                prices[symbol] = default_price
                logger.info(f"📊 Using default price for {symbol}: ${default_price}")
        
        return prices
    
    def fetch_metal_prices(self):
        """Fetch metal prices from APIs"""
        prices = {}
        
        for api in self.metal_apis:
            try:
                logger.info(f"📡 Fetching metals from {api['name']}...")
                response = requests.get(api['url'], params=api['params'], timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if api['name'] == 'MetalsAPI':
                    rates = data.get('rates', {})
                    prices['GOLD'] = 1 / rates.get('XAU', 0.0005)  # Convert to USD per oz
                    prices['SILVER'] = 1 / rates.get('XAG', 0.04)  # Convert to USD per oz
                    prices['PLATINUM'] = 1 / rates.get('XPT', 0.001)  # Convert to USD per oz
                
                logger.info(f"✅ Successfully fetched metals from {api['name']}")
                break
                
            except Exception as e:
                logger.warning(f"❌ Failed to fetch metals from {api['name']}: {e}")
                self.api_errors[api['name']] = str(e)
                continue
        
        # Use default prices for missing data
        for symbol, default_price in self.default_prices.items():
            if symbol in ['GOLD', 'SILVER', 'PLATINUM'] and symbol not in prices:
                prices[symbol] = default_price
                logger.info(f"📊 Using default price for {symbol}: ${default_price}")
        
        return prices
    
    def update_database_prices(self, crypto_prices, metal_prices):
        """Update database with new prices"""
        try:
            with transaction.atomic():
                # Update RealTimePriceFeed
                for symbol, price in crypto_prices.items():
                    try:
                        feed = RealTimePriceFeed.objects.get(symbol=symbol)
                        old_price = feed.current_price
                        feed.current_price = price
                        feed.last_updated = timezone.now()
                        feed.save()
                        
                        # Track price movement
                        if old_price != price:
                            self.track_price_movement(symbol, old_price, price)
                        
                        logger.info(f"📈 Updated {symbol}: ${old_price} → ${price}")
                        
                    except RealTimePriceFeed.DoesNotExist:
                        logger.warning(f"⚠️ Price feed not found for {symbol}")
                
                # Update InvestmentItem prices
                for symbol, price in crypto_prices.items():
                    try:
                        items = InvestmentItem.objects.filter(symbol=symbol)
                        for item in items:
                            old_price = item.current_price_usd
                            item.current_price_usd = price
                            item.last_price_update = timezone.now()
                            item.save()
                            
                            logger.info(f"💰 Updated investment item {item.name}: ${old_price} → ${price}")
                            
                    except Exception as e:
                        logger.error(f"❌ Error updating investment items for {symbol}: {e}")
                
                # Update metal prices
                for symbol, price in metal_prices.items():
                    try:
                        feed = RealTimePriceFeed.objects.get(symbol=symbol)
                        old_price = feed.current_price
                        feed.current_price = price
                        feed.last_updated = timezone.now()
                        feed.save()
                        
                        # Track price movement
                        if old_price != price:
                            self.track_price_movement(symbol, old_price, price)
                        
                        logger.info(f"📈 Updated {symbol}: ${old_price} → ${price}")
                        
                    except RealTimePriceFeed.DoesNotExist:
                        logger.warning(f"⚠️ Price feed not found for {symbol}")
                
                # Create price history records
                self.create_price_history(crypto_prices, metal_prices)
                
                logger.info("✅ Database updated successfully")
                
        except Exception as e:
            logger.error(f"❌ Error updating database: {e}")
    
    def track_price_movement(self, symbol, old_price, new_price):
        """Track price movements for statistics"""
        try:
            # Find the investment item by symbol
            try:
                item = InvestmentItem.objects.get(symbol=symbol)
            except InvestmentItem.DoesNotExist:
                logger.warning(f"⚠️ Investment item not found for symbol {symbol}")
                return
            
            stats, created = PriceMovementStats.objects.get_or_create(
                item=item,
                defaults={
                    'increases_today': 0,
                    'decreases_today': 0,
                    'unchanged_today': 0,
                    'increases_this_week': 0,
                    'decreases_this_week': 0,
                    'unchanged_this_week': 0,
                    'increases_this_month': 0,
                    'decreases_this_month': 0,
                    'unchanged_this_month': 0
                }
            )
            
            if new_price > old_price:
                stats.increases_today += 1
                stats.increases_this_week += 1
                stats.increases_this_month += 1
            elif new_price < old_price:
                stats.decreases_today += 1
                stats.decreases_this_week += 1
                stats.decreases_this_month += 1
            else:
                stats.unchanged_today += 1
                stats.unchanged_this_week += 1
                stats.unchanged_this_month += 1
            
            stats.save()
            logger.info(f"📊 Updated movement stats for {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Error tracking price movement for {symbol}: {e}")
    
    def create_price_history(self, crypto_prices, metal_prices):
        """Create price history records"""
        try:
            all_prices = {**crypto_prices, **metal_prices}
            
            for symbol, price in all_prices.items():
                try:
                    feed = RealTimePriceFeed.objects.get(symbol=symbol)
                    
                    # Create RealTimePriceHistory record
                    RealTimePriceHistory.objects.create(
                        price_feed=feed,
                        price=price,
                        timestamp=timezone.now()
                    )
                    
                    # Create PriceHistory record
                    PriceHistory.objects.create(
                        symbol=symbol,
                        price=price,
                        timestamp=timezone.now()
                    )
                    
                except RealTimePriceFeed.DoesNotExist:
                    continue
            
            logger.info("📚 Created price history records")
            
        except Exception as e:
            logger.error(f"❌ Error creating price history: {e}")
    
    def broadcast_price_updates(self):
        """Broadcast price updates via WebSocket"""
        try:
            if not self.channel_layer:
                logger.warning("⚠️ Channel layer not available")
                return
            
            # Get current prices from database
            price_feeds = RealTimePriceFeed.objects.all()
            investment_items = InvestmentItem.objects.all()
            
            price_data = []
            
            # Add price feed data
            for feed in price_feeds:
                price_data.append({
                    'symbol': feed.symbol,
                    'name': feed.name,
                    'price': float(feed.current_price),
                    'change_24h': float(feed.price_change_percentage_24h),
                    'type': 'price_feed'
                })
            
            # Add investment item data
            for item in investment_items:
                price_data.append({
                    'symbol': item.symbol,
                    'name': item.name,
                    'price': float(item.current_price_usd),
                    'change_24h': float(item.price_change_percentage_24h),
                    'type': 'investment_item'
                })
            
            # Get movement statistics
            movement_stats = {}
            for stats in PriceMovementStats.objects.all():
                movement_stats[stats.item.symbol] = {
                    'daily_increases': stats.increases_today,
                    'daily_decreases': stats.decreases_today,
                    'weekly_increases': stats.increases_this_week,
                    'weekly_decreases': stats.decreases_this_week
                }
            
            # Broadcast update
            async_to_sync(self.channel_layer.group_send)(
                'price_feeds',
                {
                    'type': 'price_update',
                    'price_data': price_data,
                    'movement_stats': movement_stats,
                    'update_count': self.update_count,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            logger.info(f"📡 Broadcasted price update with {len(price_data)} items")
            
        except Exception as e:
            logger.error(f"❌ Error broadcasting price updates: {e}")
    
    def run_price_update_cycle(self):
        """Run a complete price update cycle"""
        try:
            logger.info("🔄 Starting price update cycle...")
            
            # Fetch prices from APIs
            crypto_prices = self.fetch_crypto_prices()
            metal_prices = self.fetch_metal_prices()
            
            # Update database
            self.update_database_prices(crypto_prices, metal_prices)
            
            # Broadcast updates
            self.broadcast_price_updates()
            
            self.update_count += 1
            logger.info(f"✅ Price update cycle completed (count: {self.update_count})")
            
        except Exception as e:
            logger.error(f"❌ Error in price update cycle: {e}")
    
    def run_continuous_updates(self):
        """Run continuous price updates"""
        logger.info("🚀 Starting continuous price updates...")
        
        while self.running:
            try:
                self.run_price_update_cycle()
                
                # Wait 5 minutes before next update
                logger.info("⏰ Waiting 5 minutes for next update...")
                time.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                logger.info("🛑 Received interrupt signal, stopping...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Error in continuous updates: {e}")
                logger.info("⏰ Waiting 1 minute before retry...")
                time.sleep(60)  # Wait 1 minute before retry
        
        logger.info("🏁 Price update service stopped")

def main():
    """Main function to start the service"""
    try:
        logger.info("🎯 Starting Railway Live Price Service...")
        
        # Create and start the service
        service = RailwayLivePriceService()
        
        # Run initial update
        service.run_price_update_cycle()
        
        # Start continuous updates in a separate thread
        update_thread = Thread(target=service.run_continuous_updates, daemon=True)
        update_thread.start()
        
        logger.info("✅ Railway Live Price Service started successfully!")
        logger.info("📡 Service is now fetching live prices every 5 minutes")
        logger.info("🌐 WebSocket broadcasts are active")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down service...")
            service.running = False
            
    except Exception as e:
        logger.error(f"❌ Failed to start service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
