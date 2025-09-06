#!/usr/bin/env python3
"""
RAILWAY PRODUCTION FIX
This script ensures the live price service runs on Railway production.
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

class RailwayProductionFix:
    """Railway production fix for live price system"""
    
    def __init__(self):
        self.running = False
        self.update_interval = 30  # Update every 30 seconds
        self.channel_layer = get_channel_layer()
        self.update_count = 0
        
    def start_railway_service(self):
        """Start the Railway price service"""
        logger.info("🚀 Starting Railway Live Price Service...")
        
        # Check current state
        feeds_count = RealTimePriceFeed.objects.filter(is_active=True).count()
        items_count = InvestmentItem.objects.filter(is_active=True).count()
        
        logger.info(f"📊 Found {feeds_count} active price feeds and {items_count} investment items")
        
        # Force initial update
        logger.info("🔄 Running initial price update...")
        updated_count = price_service.update_all_prices()
        logger.info(f"✅ Initial update completed: {updated_count} prices updated")
        
        # Show current prices
        self.show_current_prices()
        
        self.running = True
        logger.info("✅ Railway Live Price Service started successfully!")
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
                        
                        # Broadcast updates
                        self.broadcast_price_updates()
                        
                        # Show current prices
                        self.show_current_prices()
                        
                        self.update_count += 1
                        logger.info(f"📊 Total updates: {self.update_count}")
                    else:
                        logger.warning("⚠️ No prices were updated")
                    
                    logger.info(f"⏰ Next update in {self.update_interval} seconds...")
                    
                except Exception as e:
                    logger.error(f"❌ Error in price update cycle: {e}")
                
                # Wait before next update
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Stopping Railway price service...")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Fatal error in continuous updates: {e}")
            self.running = False
    
    def broadcast_price_updates(self):
        """Broadcast price updates via WebSocket"""
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
            
            # Also get investment items
            items = InvestmentItem.objects.filter(is_active=True)
            for item in items:
                # Check if we already have this item from price feeds
                if not any(p['name'] == item.name for p in price_data):
                    price_data.append({
                        'symbol': item.symbol,
                        'name': item.name,
                        'current_price': float(item.current_price_usd),
                        'price_change_24h': float(item.price_change_24h) if item.price_change_24h else 0,
                        'price_change_percentage_24h': float(item.price_change_percentage_24h) if item.price_change_percentage_24h else 0,
                        'last_updated': getattr(item, 'last_price_update', item.updated_at).isoformat() if hasattr(item, 'last_price_update') and item.last_price_update else item.updated_at.isoformat(),
                        'source': 'investment_item'
                    })
            
            # Broadcast to WebSocket
            async_to_sync(self.channel_layer.group_send)(
                'price_feeds',
                {
                    'type': 'price_update',
                    'price_data': price_data,
                    'update_count': self.update_count,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            logger.info(f"📡 Broadcasted {len(price_data)} price updates via WebSocket")
            
        except Exception as e:
            logger.error(f"❌ Error broadcasting price updates: {e}")
    
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
        logger.info("🚀 RAILWAY PRODUCTION FIX STARTING...")
        
        # Create and start the service
        service = RailwayProductionFix()
        service.start_railway_service()
        
    except Exception as e:
        logger.error(f"❌ Failed to start Railway service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
