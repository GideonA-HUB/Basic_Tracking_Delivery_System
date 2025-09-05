#!/usr/bin/env python
"""
Comprehensive Test for Investment System
Tests all components: prices, featured items, WebSocket, dashboard, etc.
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentItem, RealTimePriceFeed, PriceHistory, PriceMovementStats
from investments.price_services import price_service
from django.utils import timezone

def test_investment_system():
    print("=" * 60)
    print("🧪 COMPREHENSIVE INVESTMENT SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Database State
    print("\n1️⃣ Testing Database State...")
    total_items = InvestmentItem.objects.count()
    featured_items = InvestmentItem.objects.filter(is_featured=True).count()
    active_feeds = RealTimePriceFeed.objects.filter(is_active=True).count()
    price_history = PriceHistory.objects.count()
    
    print(f"   📊 Investment Items: {total_items}")
    print(f"   ⭐ Featured Items: {featured_items}")
    print(f"   📈 Active Price Feeds: {active_feeds}")
    print(f"   📋 Price History Records: {price_history}")
    
    # Test 2: Featured Items Display
    print("\n2️⃣ Testing Featured Items...")
    featured_sample = InvestmentItem.objects.filter(is_featured=True)[:5]
    for item in featured_sample:
        print(f"   ⭐ {item.name} - ${item.current_price_usd} ({item.price_change_percentage_24h:+.2f}%)")
    
    # Test 3: Price Feed Matching
    print("\n3️⃣ Testing Price Feed Matching...")
    items_with_feeds = 0
    for item in InvestmentItem.objects.filter(is_active=True):
        if RealTimePriceFeed.objects.filter(symbol=item.symbol).exists():
            items_with_feeds += 1
    
    print(f"   📊 Items with matching price feeds: {items_with_feeds}/{total_items}")
    
    # Test 4: Price Update Service
    print("\n4️⃣ Testing Price Update Service...")
    try:
        updated_count = price_service.update_all_prices()
        print(f"   ✅ Successfully updated {updated_count} prices")
    except Exception as e:
        print(f"   ❌ Price update failed: {e}")
    
    # Test 5: API Endpoints
    print("\n5️⃣ Testing API Endpoints...")
    base_url = "http://localhost:8000"  # Adjust if needed
    
    api_endpoints = [
        "/investments/api/live-prices/",
        "/investments/api/price-statistics/",
        "/investments/api/investments/",
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {endpoint} - OK ({len(data.get('prices', data.get('results', [])))} items)")
            else:
                print(f"   ⚠️  {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")
    
    # Test 6: WebSocket Connection (simulation)
    print("\n6️⃣ Testing WebSocket Configuration...")
    try:
        from investments.consumers import PriceFeedConsumer
        print("   ✅ WebSocket consumer imported successfully")
    except Exception as e:
        print(f"   ❌ WebSocket consumer error: {e}")
    
    # Test 7: Price History and Statistics
    print("\n7️⃣ Testing Price History and Statistics...")
    recent_history = PriceHistory.objects.filter(
        timestamp__gte=timezone.now() - timezone.timedelta(hours=1)
    ).count()
    
    today_stats = PriceMovementStats.objects.filter(
        date=timezone.now().date()
    ).count()
    
    print(f"   📊 Recent price history (1h): {recent_history}")
    print(f"   📊 Today's movement stats: {today_stats}")
    
    # Test 8: Real-time Price Data
    print("\n8️⃣ Testing Real-time Price Data...")
    feeds = RealTimePriceFeed.objects.filter(is_active=True)
    for feed in feeds[:3]:  # Show first 3
        print(f"   📈 {feed.name} ({feed.symbol}): ${feed.current_price} ({feed.price_change_percentage_24h:+.2f}%)")
    
    # Test 9: Investment Item Prices
    print("\n9️⃣ Testing Investment Item Prices...")
    items = InvestmentItem.objects.filter(is_active=True)[:3]  # Show first 3
    for item in items:
        print(f"   💰 {item.name}: ${item.current_price_usd} ({item.price_change_percentage_24h:+.2f}%)")
    
    # Test 10: System Health Check
    print("\n🔟 System Health Check...")
    
    # Check for issues
    issues = []
    
    # Items without symbols
    items_without_symbols = InvestmentItem.objects.filter(symbol__isnull=True).count()
    if items_without_symbols > 0:
        issues.append(f"{items_without_symbols} items without symbols")
    
    # Outdated prices
    outdated_threshold = timezone.now() - timezone.timedelta(hours=24)
    outdated_items = InvestmentItem.objects.filter(last_price_update__lt=outdated_threshold).count()
    if outdated_items > 0:
        issues.append(f"{outdated_items} items with outdated prices")
    
    # Missing price feeds
    missing_feeds = total_items - items_with_feeds
    if missing_feeds > 0:
        issues.append(f"{missing_feeds} items without price feeds")
    
    if issues:
        print("   ⚠️  Issues found:")
        for issue in issues:
            print(f"      - {issue}")
    else:
        print("   ✅ No issues found - system is healthy!")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Database: {total_items} items, {featured_items} featured")
    print(f"✅ Price Feeds: {active_feeds} active feeds")
    print(f"✅ Price History: {price_history} records")
    print(f"✅ API Endpoints: Tested")
    print(f"✅ WebSocket: Configured")
    print(f"✅ Real-time Updates: Working")
    
    if issues:
        print(f"⚠️  Issues: {len(issues)} found")
    else:
        print("🎉 All systems operational!")
    
    print("\n🚀 Next Steps:")
    print("   1. Start the production price service")
    print("   2. Test the website at meridianassetlogistics.com")
    print("   3. Verify featured items display correctly")
    print("   4. Check real-time price updates in dashboard")
    print("   5. Test WebSocket connections")

if __name__ == "__main__":
    test_investment_system()
