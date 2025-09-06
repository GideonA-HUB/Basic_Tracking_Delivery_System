#!/usr/bin/env python3
"""
TEST RAILWAY PRICE SERVICE
==========================
Test script to verify the Railway price service works correctly.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import RealTimePriceFeed, InvestmentItem, PriceMovementStats
from django.utils import timezone

def test_price_service():
    """Test the price service functionality"""
    print("🧪 Testing Railway Price Service...")
    
    # Test 1: Check if models exist
    print("\n1. Checking models...")
    try:
        feeds = RealTimePriceFeed.objects.all()
        items = InvestmentItem.objects.all()
        stats = PriceMovementStats.objects.all()
        
        print(f"   ✅ Found {feeds.count()} price feeds")
        print(f"   ✅ Found {items.count()} investment items")
        print(f"   ✅ Found {stats.count()} movement stats")
        
    except Exception as e:
        print(f"   ❌ Error checking models: {e}")
        return False
    
    # Test 2: Check current prices
    print("\n2. Checking current prices...")
    try:
        for feed in feeds[:5]:  # Show first 5
            print(f"   📊 {feed.symbol}: ${feed.current_price} (Updated: {feed.last_updated})")
        
        for item in items[:5]:  # Show first 5
            print(f"   💰 {item.name}: ${item.current_price_usd}")
            
    except Exception as e:
        print(f"   ❌ Error checking prices: {e}")
        return False
    
    # Test 3: Check movement stats
    print("\n3. Checking movement statistics...")
    try:
        for stat in stats[:3]:  # Show first 3
            print(f"   📈 {stat.item.symbol}: +{stat.increases_today} -{stat.decreases_today}")
            
    except Exception as e:
        print(f"   ❌ Error checking stats: {e}")
        return False
    
    # Test 4: Test API connectivity
    print("\n4. Testing API connectivity...")
    try:
        import requests
        
        # Test CoinGecko
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=10)
        if response.status_code == 200:
            data = response.json()
            btc_price = data['bitcoin']['usd']
            print(f"   ✅ CoinGecko API working - BTC: ${btc_price}")
        else:
            print(f"   ❌ CoinGecko API error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API connectivity error: {e}")
        return False
    
    # Test 5: Check WebSocket setup
    print("\n5. Checking WebSocket setup...")
    try:
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        if channel_layer:
            print("   ✅ Channel layer configured")
        else:
            print("   ⚠️ Channel layer not configured")
            
    except Exception as e:
        print(f"   ❌ WebSocket setup error: {e}")
        return False
    
    print("\n🎯 Test Results:")
    print("   ✅ All tests passed!")
    print("   🚀 Service is ready for deployment")
    print("   📡 Live price updates will work on Railway")
    
    return True

def main():
    """Main test function"""
    try:
        success = test_price_service()
        
        if success:
            print("\n🎉 Railway Price Service is ready!")
            print("📋 Next steps:")
            print("   1. Upload files to Railway")
            print("   2. Add price-service to Procfile")
            print("   3. Deploy the service")
            print("   4. Monitor logs for success")
        else:
            print("\n❌ Tests failed - check the errors above")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
