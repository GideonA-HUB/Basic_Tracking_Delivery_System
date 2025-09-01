#!/usr/bin/env python3
"""
Script to set up real-time price feeds and start live updates
"""

import os
import sys
import django
from decimal import Decimal
import time
import threading

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import RealTimePriceFeed, InvestmentItem
from investments.price_services import price_service, update_real_time_prices


def setup_price_feeds():
    """Set up initial price feeds"""
    print("Setting up real-time price feeds...")
    
    price_feeds_data = [
        {
            'name': 'Bitcoin (BTC)',
            'symbol': 'BTC',
            'asset_type': 'crypto',
            'current_price': Decimal('45000.00'),
            'base_currency': 'USD',
            'is_active': True
        },
        {
            'name': 'Ethereum (ETH)',
            'symbol': 'ETH',
            'asset_type': 'crypto',
            'current_price': Decimal('2800.00'),
            'base_currency': 'USD',
            'is_active': True
        },
        {
            'name': 'Cardano (ADA)',
            'symbol': 'ADA',
            'asset_type': 'crypto',
            'current_price': Decimal('0.45'),
            'base_currency': 'USD',
            'is_active': True
        },
        {
            'name': 'Gold (XAU)',
            'symbol': 'XAU',
            'asset_type': 'precious_metal',
            'current_price': Decimal('1950.00'),
            'base_currency': 'USD',
            'is_active': True
        },
        {
            'name': 'Silver (XAG)',
            'symbol': 'XAG',
            'asset_type': 'precious_metal',
            'current_price': Decimal('24.50'),
            'base_currency': 'USD',
            'is_active': True
        },
        {
            'name': 'Platinum (XPT)',
            'symbol': 'XPT',
            'asset_type': 'precious_metal',
            'current_price': Decimal('920.00'),
            'base_currency': 'USD',
            'is_active': True
        },
        {
            'name': 'Real Estate Index',
            'symbol': 'REIT_INDEX',
            'asset_type': 'real_estate',
            'current_price': Decimal('1500.00'),
            'base_currency': 'USD',
            'is_active': True
        },
        {
            'name': 'Property Fund',
            'symbol': 'PROPERTY_FUND',
            'asset_type': 'real_estate',
            'current_price': Decimal('2500.00'),
            'base_currency': 'USD',
            'is_active': True
        }
    ]
    
    created_feeds = []
    for feed_data in price_feeds_data:
        feed, created = RealTimePriceFeed.objects.get_or_create(
            symbol=feed_data['symbol'],
            defaults=feed_data
        )
        if created:
            print(f"✅ Created price feed: {feed.name} ({feed.symbol})")
        else:
            print(f"ℹ️  Price feed already exists: {feed.name} ({feed.symbol})")
        created_feeds.append(feed)
    
    return created_feeds


def run_live_updates():
    """Run continuous live price updates"""
    print("\n🚀 Starting live price updates...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            print(f"\n⏰ {time.strftime('%Y-%m-%d %H:%M:%S')} - Updating prices...")
            
            # Update all prices
            updated_count = update_real_time_prices()
            
            if updated_count > 0:
                print(f"✅ Updated {updated_count} price feeds")
            else:
                print("⚠️  No price updates made")
            
            # Wait 30 seconds before next update
            print("⏳ Waiting 30 seconds for next update...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Live updates stopped by user")
    except Exception as e:
        print(f"❌ Error in live updates: {e}")


def run_background_updates():
    """Run updates in background thread"""
    def update_loop():
        while True:
            try:
                update_real_time_prices()
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                print(f"Background update error: {e}")
                time.sleep(60)  # Wait longer on error
    
    thread = threading.Thread(target=update_loop, daemon=True)
    thread.start()
    print("🔄 Background price updates started")
    return thread


def main():
    """Main function"""
    print("🚀 SETTING UP REAL-TIME PRICE FEEDS")
    print("=" * 60)
    
    try:
        # Set up price feeds
        feeds = setup_price_feeds()
        
        print(f"\n📊 SUMMARY:")
        print(f"   - Price feeds created: {len(feeds)}")
        
        print(f"\n📋 ACTIVE PRICE FEEDS:")
        for feed in feeds:
            print(f"   - {feed.name} ({feed.symbol}): ${feed.current_price}")
        
        # Initial price update
        print(f"\n🔄 Running initial price update...")
        updated_count = update_real_time_prices()
        print(f"✅ Initial update completed: {updated_count} feeds updated")
        
        print(f"\n🌐 NEXT STEPS:")
        print("   1. Real-time price feeds are now active")
        print("   2. Prices will update automatically every 30 seconds")
        print("   3. Investment items will reflect live price changes")
        print("   4. Portfolio values will update in real-time")
        
        # Ask user if they want to run live updates
        response = input("\n❓ Do you want to run live updates now? (y/n): ").lower().strip()
        
        if response == 'y':
            run_live_updates()
        else:
            print("💡 To start live updates later, run: python setup_real_time_prices.py --live")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--live':
        # Run only live updates
        run_live_updates()
    else:
        # Run full setup
        main()
