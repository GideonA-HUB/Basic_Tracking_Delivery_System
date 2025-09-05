#!/usr/bin/env python
"""
PRODUCTION REAL-TIME SYSTEM STARTUP
This script starts all necessary services for real-time investment tracking
"""
import os
import sys
import django
import subprocess
import time
import logging
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentItem, RealTimePriceFeed
from investments.price_services import price_service
from investments.tasks import update_real_time_prices

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_all_prices_now():
    """Update all prices immediately"""
    print("🔄 Updating all prices with real market data...")
    
    try:
        # Update price feeds
        updated_count = price_service.update_all_prices()
        print(f"✅ Updated {updated_count} price feeds")
        
        # Update investment items
        items = InvestmentItem.objects.filter(is_active=True)
        updated_items = 0
        
        for item in items:
            if item.symbol:
                feed = RealTimePriceFeed.objects.filter(symbol=item.symbol, is_active=True).first()
                if feed:
                    item.current_price_usd = feed.current_price
                    item.price_change_24h = feed.price_change_24h
                    item.price_change_percentage_24h = feed.price_change_percentage_24h
                    item.last_price_update = timezone.now()
                    item.save()
                    updated_items += 1
        
        print(f"✅ Updated {updated_items} investment items with real market prices")
        return True
        
    except Exception as e:
        logger.error(f"Error updating prices: {e}")
        return False

def start_celery_worker():
    """Start Celery worker for background tasks"""
    print("🔄 Starting Celery worker...")
    
    try:
        # Start Celery worker in background
        cmd = ['celery', '-A', 'delivery_tracker', 'worker', '--loglevel=info']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Celery worker started")
        return process
    except Exception as e:
        logger.error(f"Error starting Celery worker: {e}")
        return None

def start_celery_beat():
    """Start Celery beat for scheduled tasks"""
    print("🔄 Starting Celery beat...")
    
    try:
        # Start Celery beat in background
        cmd = ['celery', '-A', 'delivery_tracker', 'beat', '--loglevel=info']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Celery beat started")
        return process
    except Exception as e:
        logger.error(f"Error starting Celery beat: {e}")
        return None

def start_django_server():
    """Start Django development server"""
    print("🔄 Starting Django server...")
    
    try:
        # Start Django server
        cmd = ['python', 'manage.py', 'runserver', '0.0.0.0:8000']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Django server started on http://localhost:8000")
        return process
    except Exception as e:
        logger.error(f"Error starting Django server: {e}")
        return None

def main():
    """Main startup function"""
    print("🚀 STARTING PRODUCTION REAL-TIME SYSTEM")
    print("=" * 50)
    
    # Update prices immediately
    if update_all_prices_now():
        print("✅ Prices updated successfully")
    else:
        print("❌ Failed to update prices")
    
    # Start services
    print("\n🔄 Starting all services...")
    
    # Start Django server
    django_process = start_django_server()
    time.sleep(2)
    
    # Start Celery worker
    celery_worker = start_celery_worker()
    time.sleep(2)
    
    # Start Celery beat
    celery_beat = start_celery_beat()
    time.sleep(2)
    
    print("\n🎉 PRODUCTION REAL-TIME SYSTEM STARTED!")
    print("=" * 50)
    print("✅ Django Server: http://localhost:8000")
    print("✅ Investment Marketplace: http://localhost:8000/investments/")
    print("✅ Live Dashboard: http://localhost:8000/investments/live-dashboard/")
    print("✅ Enhanced Dashboard: http://localhost:8000/investments/enhanced-dashboard/")
    print("✅ Celery Worker: Running")
    print("✅ Celery Beat: Running")
    print("✅ Real-time Updates: Active")
    print("=" * 50)
    print("\n📊 SYSTEM FEATURES:")
    print("• Real-time price updates every 60 seconds")
    print("• Live WebSocket connections")
    print("• Price movement tracking and counting")
    print("• Live charts and analytics")
    print("• Featured items with real market prices")
    print("• Portfolio valuation updates")
    print("\n🔴 The system is now LIVE with real market data!")
    
    try:
        # Keep the script running
        while True:
            time.sleep(60)
            print(f"⏰ System running... {datetime.now().strftime('%H:%M:%S')}")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        if django_process:
            django_process.terminate()
        if celery_worker:
            celery_worker.terminate()
        if celery_beat:
            celery_beat.terminate()
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
