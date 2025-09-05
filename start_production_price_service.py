#!/usr/bin/env python
"""
Production Live Price Update Service
Starts a continuous service to update prices without Redis dependency
"""
import os
import sys
import django
import time
import logging
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentItem, RealTimePriceFeed
from investments.price_services import price_service
from django.utils import timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_price_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionPriceService:
    def __init__(self, update_interval=60):
        self.update_interval = update_interval
        self.running = False
        self.update_count = 0
        self.last_update_time = None
        
    def start(self):
        """Start the production price service"""
        logger.info("Starting Production Live Price Service")
        logger.info(f"Update interval: {self.update_interval} seconds")
        logger.info("Press Ctrl+C to stop")
        
        self.running = True
        
        try:
            while self.running:
                self.run_update_cycle()
                time.sleep(self.update_interval)
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Service error: {e}")
            self.running = False
    
    def run_update_cycle(self):
        """Run a single update cycle"""
        try:
            start_time = time.time()
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            logger.info(f"[{timestamp}] Starting price update cycle...")
            
            # Update all prices
            updated_count = price_service.update_all_prices()
            
            # Update investment item prices
            price_service.update_investment_item_prices()
            
            # Update counters
            self.update_count += 1
            self.last_update_time = timezone.now()
            
            # Calculate cycle time
            cycle_time = time.time() - start_time
            
            logger.info(f"[{timestamp}] Update cycle completed")
            logger.info(f"   Updated {updated_count} prices")
            logger.info(f"   Cycle time: {cycle_time:.2f}s")
            logger.info(f"   Total cycles: {self.update_count}")
            
        except Exception as e:
            timestamp = datetime.now().strftime('%H:%M:%S')
            logger.error(f"[{timestamp}] Update cycle failed: {e}")
    
    def stop(self):
        """Stop the service"""
        logger.info("Stopping Production Live Price Service...")
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
    
    parser = argparse.ArgumentParser(description='Production Live Price Update Service')
    parser.add_argument('--interval', type=int, default=60, help='Update interval in seconds (default: 60)')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    
    args = parser.parse_args()
    
    service = ProductionPriceService(update_interval=args.interval)
    
    if args.once:
        logger.info("Running single update cycle...")
        service.run_update_cycle()
        logger.info("Single update completed")
    else:
        service.start()

if __name__ == "__main__":
    main()
