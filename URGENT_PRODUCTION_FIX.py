#!/usr/bin/env python3
"""
URGENT PRODUCTION FIX
This script fixes the production live price system immediately.
The issue is that the price service is not running on production.
"""

import os
import sys
import django
import time
import logging
import threading
from datetime import datetime

# Setup Django - use local settings for testing, production for Railway
if 'RAILWAY_ENVIRONMENT' in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings_production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.utils import timezone
from investments.price_services import price_service
from investments.models import RealTimePriceFeed, InvestmentItem
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UrgentProductionFix:
    """Urgent fix for production live price system"""
    
    def __init__(self):
        self.running = False
        self.update_interval = 30  # Update every 30 seconds
        self.channel_layer = get_channel_layer()
        
    def fix_production_system(self):
        """Fix the production system immediately"""
        logger.info("🚨 URGENT: Fixing production live price system...")
        
        # Step 1: Update all prices immediately
        logger.info("📊 Step 1: Updating all prices from APIs...")
        updated_count = price_service.update_all_prices()
        logger.info(f"✅ Updated {updated_count} prices")
        
        # Step 2: Verify prices are correct
        logger.info("🔍 Step 2: Verifying prices...")
        self.verify_prices()
        
        # Step 3: Start continuous updates
        logger.info("🔄 Step 3: Starting continuous price updates...")
        self.start_continuous_updates()
        
    def verify_prices(self):
        """Verify that prices are correct"""
        try:
            # Check Bitcoin price
            btc_feed = RealTimePriceFeed.objects.filter(symbol='BTC').first()
            if btc_feed:
                logger.info(f"💰 Bitcoin: ${btc_feed.current_price:,.2f}")
                if btc_feed.current_price < 100000:  # If less than $100k, it's probably wrong
                    logger.warning("⚠️ Bitcoin price seems too low, updating...")
                    self.force_update_crypto_prices()
            
            # Check Ethereum price
            eth_feed = RealTimePriceFeed.objects.filter(symbol='ETH').first()
            if eth_feed:
                logger.info(f"💰 Ethereum: ${eth_feed.current_price:,.2f}")
                
        except Exception as e:
            logger.error(f"❌ Error verifying prices: {e}")
    
    def force_update_crypto_prices(self):
        """Force update crypto prices from APIs"""
        try:
            logger.info("🔄 Force updating crypto prices...")
            crypto_prices = price_service.fetch_crypto_prices()
            
            for symbol, price_data in crypto_prices.items():
                feed = RealTimePriceFeed.objects.filter(symbol=symbol).first()
                if feed:
                    old_price = feed.current_price
                    new_price = price_data['price']
                    
                    feed.current_price = new_price
                    feed.price_change_24h = price_data['change_24h']
                    feed.price_change_percentage_24h = (price_data['change_24h'] / old_price * 100) if old_price > 0 else 0
                    feed.last_updated = timezone.now()
                    feed.save()
                    
                    logger.info(f"✅ Updated {symbol}: ${old_price:,.2f} → ${new_price:,.2f}")
                    
        except Exception as e:
            logger.error(f"❌ Error force updating crypto prices: {e}")
    
    def start_continuous_updates(self):
        """Start continuous price updates"""
        self.running = True
        logger.info("🚀 Starting continuous price updates...")
        
        # Start update thread
        update_thread = threading.Thread(target=self.update_loop, daemon=True)
        update_thread.start()
        
        # Start broadcast thread
        broadcast_thread = threading.Thread(target=self.broadcast_loop, daemon=True)
        broadcast_thread.start()
        
        logger.info("✅ Continuous updates started!")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping updates...")
            self.running = False
    
    def update_loop(self):
        """Main update loop"""
        while self.running:
            try:
                logger.info("🔄 Running price update cycle...")
                
                # Update all prices
                updated_count = price_service.update_all_prices()
                
                if updated_count > 0:
                    logger.info(f"✅ Updated {updated_count} prices successfully")
                    
                    # Show current major prices
                    self.show_current_prices()
                else:
                    logger.warning("⚠️ No prices were updated")
                
                # Wait before next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in update loop: {e}")
                time.sleep(60)  # Wait 1 minute before retry
    
    def broadcast_loop(self):
        """Broadcast updates via WebSocket"""
        while self.running:
            try:
                # Get current prices
                feeds = RealTimePriceFeed.objects.filter(is_active=True)
                price_data = []
                
                for feed in feeds:
                    price_data.append({
                        'symbol': feed.symbol,
                        'name': feed.name,
                        'current_price': float(feed.current_price),
                        'price_change_24h': float(feed.price_change_24h),
                        'price_change_percentage_24h': float(feed.price_change_percentage_24h),
                        'last_updated': feed.last_updated.isoformat() if feed.last_updated else None,
                        'source': 'price_feed'
                    })
                
                # Broadcast to WebSocket
                async_to_sync(self.channel_layer.group_send)(
                    'price_feeds',
                    {
                        'type': 'price_update',
                        'price_data': price_data,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
                logger.info(f"📡 Broadcasted {len(price_data)} price updates")
                
                # Wait before next broadcast
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Error in broadcast loop: {e}")
                time.sleep(60)
    
    def show_current_prices(self):
        """Show current major cryptocurrency prices"""
        try:
            major_coins = ['BTC', 'ETH', 'ADA', 'SOL']
            feeds = RealTimePriceFeed.objects.filter(symbol__in=major_coins, is_active=True)
            
            logger.info("💰 Current major cryptocurrency prices:")
            for feed in feeds:
                logger.info(f"   {feed.name}: ${feed.current_price:,.2f} ({feed.price_change_percentage_24h:+.2f}%)")
                
        except Exception as e:
            logger.error(f"Error showing current prices: {e}")

def main():
    """Main function"""
    try:
        logger.info("🚨 URGENT PRODUCTION FIX STARTING...")
        
        # Create and run the fix
        fix = UrgentProductionFix()
        fix.fix_production_system()
        
    except Exception as e:
        logger.error(f"❌ Failed to fix production system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
