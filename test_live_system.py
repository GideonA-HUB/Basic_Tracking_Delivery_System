#!/usr/bin/env python3
"""
Test Live System
Quick test to verify the live price system is working
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.utils import timezone
from investments.models import RealTimePriceFeed, InvestmentItem, PriceMovementStats

def test_system():
    print("🧪 Testing Live Price System...")
    print("=" * 50)
    
    # Test 1: Check price feeds
    print("1. Checking price feeds...")
    feeds = RealTimePriceFeed.objects.filter(is_active=True)
    print(f"   ✅ Found {feeds.count()} active price feeds")
    
    for feed in feeds[:5]:  # Show first 5
        print(f"   📊 {feed.symbol}: ${feed.current_price} ({feed.price_change_percentage_24h:+.2f}%)")
    
    # Test 2: Check investment items
    print("\n2. Checking investment items...")
    items = InvestmentItem.objects.all()
    print(f"   ✅ Found {items.count()} investment items")
    
    for item in items[:5]:  # Show first 5
        print(f"   💰 {item.name}: ${item.current_price_usd}")
    
    # Test 3: Check movement statistics
    print("\n3. Checking movement statistics...")
    today = timezone.now().date()
    stats = PriceMovementStats.objects.filter(date=today).first()
    
    if stats:
        print(f"   📈 Increases today: {stats.increases_today}")
        print(f"   📉 Decreases today: {stats.decreases_today}")
        print(f"   📊 Total movements: {stats.total_movements_today}")
        print(f"   🔄 Net movement: {stats.net_movement_today}")
    else:
        print("   ⚠️  No movement statistics found for today")
    
    # Test 4: Check recent price history
    print("\n4. Checking recent price history...")
    from investments.models import RealTimePriceHistory
    recent_history = RealTimePriceHistory.objects.order_by('-timestamp')[:5]
    
    if recent_history:
        print(f"   ✅ Found {recent_history.count()} recent price updates")
        for history in recent_history:
            print(f"   📈 {history.price_feed.symbol}: ${history.price} ({history.change_percentage:+.2f}%)")
    else:
        print("   ⚠️  No recent price history found")
    
    print("\n🎯 System Status:")
    if feeds.count() > 0 and items.count() > 0:
        print("   ✅ System is working - prices are available")
        print("   🌐 Check your website for live updates")
        print("   📡 WebSocket should be broadcasting changes")
    else:
        print("   ❌ System needs setup - no price data found")
    
    return True

if __name__ == "__main__":
    test_system()
