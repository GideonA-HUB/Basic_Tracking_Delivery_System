#!/usr/bin/env python
"""
Live Price Update Service
Starts a continuous service to update prices and broadcast via WebSocket
"""
import os
import sys
import django
import asyncio
import time
import logging
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentItem, RealTimePriceFeed
from investments.price_services import price_service
from investments.tasks import broadcast_price_updates
from django.utils import timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_price_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LivePriceService:
    def __init__(self, update_interval=60):
        self.update_interval = update_interval
        self.running = False
        self.update_count = 0
        self.last_update_time = None
        
    def start(self):
        """Start the live price service"""
        logger.info("🚀 Starting Live Price Service")
        logger.info(f"📊 Update interval: {self.update_interval} seconds")
        logger.info("🔄 Press Ctrl+C to stop")
        
        self.running = True
        
        try:
            while self.running:
                self.run_update_cycle()
                time.sleep(self.update_interval)
        except KeyboardInterrupt:
            logger.info("⏹️  Service stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Service error: {e}")
            self.running = False
    
    def run_update_cycle(self):
        """Run a single update cycle"""
        try:
            start_time = time.time()
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            logger.info(f"[{timestamp}] 🔄 Starting price update cycle...")
            
            # Update all prices
            updated_count = price_service.update_all_prices()
            
            # Update investment item prices
            price_service.update_investment_item_prices()
            
            # Get live price updates for broadcasting
            price_updates = self.get_live_price_updates()
            
            # Broadcast updates via WebSocket (non-blocking)
            try:
                broadcast_price_updates.delay(price_updates)
                logger.info(f"[{timestamp}] 📡 Broadcasted {len(price_updates)} price updates")
            except Exception as ws_error:
                logger.warning(f"[{timestamp}] ⚠️  WebSocket broadcast failed: {ws_error}")
            
            # Update counters
            self.update_count += 1
            self.last_update_time = timezone.now()
            
            # Calculate cycle time
            cycle_time = time.time() - start_time
            
            logger.info(f"[{timestamp}] ✅ Update cycle completed")
            logger.info(f"   📊 Updated {updated_count} prices")
            logger.info(f"   📡 Broadcasted {len(price_updates)} updates")
            logger.info(f"   ⏱️  Cycle time: {cycle_time:.2f}s")
            logger.info(f"   🔢 Total cycles: {self.update_count}")
            
        except Exception as e:
            timestamp = datetime.now().strftime('%H:%M:%S')
            logger.error(f"[{timestamp}] ❌ Update cycle failed: {e}")
    
    def get_live_price_updates(self):
        """Get live price updates for broadcasting"""
        try:
            feeds = RealTimePriceFeed.objects.filter(is_active=True)
            updates = []
            
            for feed in feeds:
                updates.append({
                    'symbol': feed.symbol,
                    'name': feed.name,
                    'price': float(feed.current_price),
                    'change_24h': float(feed.price_change_24h),
                    'change_percentage': float(feed.price_change_percentage_24h),
                    'last_updated': feed.last_updated.isoformat() if feed.last_updated else None
                })
            
            return updates
            
        except Exception as e:
            logger.error(f"Error getting live price updates: {e}")
            return []
    
    def stop(self):
        """Stop the service"""
        logger.info("🛑 Stopping Live Price Service...")
        self.running = False
    
    def get_status(self):
        """Get service status"""
        return {
            'running': self.running,
            'update_count': self.update_count,
            'last_update_time': self.last_update_time.isoformat() if self.last_update_time else None,
            'update_interval': self.update_interval
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Live Price Update Service')
    parser.add_argument('--interval', type=int, default=60, help='Update interval in seconds (default: 60)')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    
    args = parser.parse_args()
    
    service = LivePriceService(update_interval=args.interval)
    
    if args.once:
        logger.info("🔄 Running single update cycle...")
        service.run_update_cycle()
        logger.info("✅ Single update completed")
    else:
        service.start()

if __name__ == "__main__":
    main()
