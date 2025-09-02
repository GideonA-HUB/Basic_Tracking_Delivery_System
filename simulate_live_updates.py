#!/usr/bin/env python3
"""
Script to simulate real-time price updates for the investment system
Run this periodically to see live price updates in action
"""

import os
import sys
import django
import random
import time
import asyncio
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.utils import timezone
from investments.models import RealTimePriceFeed, InvestmentItem
from investments.consumers import PriceFeedConsumer

def simulate_price_updates():
    """Simulate realistic price updates for all assets"""
    print("🔄 SIMULATING REAL-TIME PRICE UPDATES")
    print("=" * 50)
    
    # Update real-time price feeds
    price_feeds = RealTimePriceFeed.objects.filter(is_active=True)
    
    for feed in price_feeds:
        current_price = float(feed.current_price)
        
        # Simulate realistic price movements (small changes)
        price_change_percent = random.uniform(-2.0, 2.0)  # ±2% max change
        price_change_amount = current_price * (price_change_percent / 100)
        new_price = current_price + price_change_amount
        
        # Update the price feed
        feed.update_price(
            Decimal(str(new_price)),
            Decimal(str(price_change_amount)),
            Decimal(str(price_change_percent))
        )
        
        print(f"📈 {feed.name}: ${new_price:.2f} ({price_change_percent:+.2f}%)")
    
    # Update investment item prices
    investment_items = InvestmentItem.objects.filter(is_active=True)
    
    for item in investment_items:
        # Find matching price feed
        matching_feed = None
        for feed in price_feeds:
            if feed.name == item.name or (feed.symbol and item.symbol and feed.symbol == item.symbol):
                matching_feed = feed
                break
        
        if matching_feed:
            # Update item price to match feed
            old_price = float(item.current_price_usd)
            new_price = float(matching_feed.current_price)
            
            if abs(new_price - old_price) > 0.01:  # Only update if change is significant
                item.current_price_usd = new_price
                item.price_change_24h = matching_feed.price_change_24h
                item.price_change_percentage_24h = matching_feed.price_change_percentage_24h
                item.last_price_update = timezone.now()
                item.save()
                
                print(f"💎 {item.name}: ${old_price:.2f} → ${new_price:.2f}")
    
    print("✅ Price simulation completed!")

async def broadcast_updates():
    """Broadcast price updates via WebSocket"""
    try:
        print("📡 Broadcasting price updates via WebSocket...")
        
        # Get updated price data
        feeds = RealTimePriceFeed.objects.filter(is_active=True)
        price_data = []
        
        for feed in feeds:
            price_data.append({
                'symbol': feed.symbol,
                'name': feed.name,
                'current_price': float(feed.current_price),
                'price_change_24h': float(feed.price_change_24h),
                'price_change_percentage_24h': float(feed.price_change_percentage_24h),
                'last_updated': feed.last_updated.isoformat() if feed.last_updated else None
            })
        
        # Broadcast to all connected clients
        await PriceFeedConsumer.broadcast_price_update(price_data)
        print(f"✅ Broadcasted {len(price_data)} price updates")
        
    except Exception as e:
        print(f"❌ Error broadcasting updates: {e}")

def run_continuous_simulation(interval_seconds=30, max_updates=20):
    """Run continuous price updates"""
    print(f"🚀 Starting continuous price simulation (every {interval_seconds} seconds)")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    update_count = 0
    
    try:
        while update_count < max_updates:
            update_count += 1
            print(f"\n🔄 Update #{update_count} at {timezone.now().strftime('%H:%M:%S')}")
            
            # Simulate price updates
            simulate_price_updates()
            
            # Try to broadcast updates
            try:
                asyncio.run(broadcast_updates())
            except Exception as e:
                print(f"⚠️ Broadcasting failed: {e}")
            
            if update_count < max_updates:
                print(f"⏳ Waiting {interval_seconds} seconds until next update...")
                time.sleep(interval_seconds)
        
        print(f"\n✅ Completed {update_count} price updates")
        
    except KeyboardInterrupt:
        print("\n⏹️ Simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simulate live price updates')
    parser.add_argument('--interval', type=int, default=30, help='Update interval in seconds (default: 30)')
    parser.add_argument('--max-updates', type=int, default=20, help='Maximum number of updates (default: 20)')
    parser.add_argument('--single', action='store_true', help='Run single update instead of continuous')
    
    args = parser.parse_args()
    
    if args.single:
        print("🔄 Running single price update...")
        simulate_price_updates()
        try:
            asyncio.run(broadcast_updates())
        except Exception as e:
            print(f"⚠️ Broadcasting failed: {e}")
    else:
        run_continuous_simulation(args.interval, args.max_updates)

if __name__ == "__main__":
    main()
