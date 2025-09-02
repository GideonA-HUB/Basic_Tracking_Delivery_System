#!/usr/bin/env python
"""
Simple WebSocket test script to verify the connection works
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')

# Initialize Django
django.setup()

def test_models():
    """Test if models can be accessed"""
    print("🧪 Testing Model Access...")
    
    try:
        from investments.models import RealTimePriceFeed, InvestmentItem
        
        feeds = RealTimePriceFeed.objects.filter(is_active=True)
        items = InvestmentItem.objects.filter(is_active=True)
        
        print(f"✅ Found {feeds.count()} price feeds")
        print(f"✅ Found {items.count()} investment items")
        
        # Show some examples
        print("\n📊 Sample Price Feeds:")
        for feed in feeds[:3]:
            print(f"  - {feed.name} ({feed.symbol}): ${feed.current_price}")
        
        print("\n💎 Sample Investment Items:")
        for item in items[:3]:
            print(f"  - {item.name}: ${item.current_price_usd}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing models: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_consumer_import():
    """Test if consumer can be imported"""
    print("\n🧪 Testing Consumer Import...")
    
    try:
        from investments.consumers import PriceFeedConsumer
        print("✅ PriceFeedConsumer imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error importing consumer: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_websocket_routing():
    """Test if WebSocket routing is configured"""
    print("\n🧪 Testing WebSocket Routing...")
    
    try:
        from investments.routing import websocket_urlpatterns
        print(f"✅ Found {len(websocket_urlpatterns)} WebSocket URL patterns")
        
        for pattern in websocket_urlpatterns:
            print(f"  - {pattern.pattern}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking routing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 WebSocket System Test")
    print("=" * 50)
    
    tests = [
        test_models,
        test_consumer_import,
        test_websocket_routing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n🎯 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed! WebSocket system should work.")
        print("\n💡 Next steps:")
        print("1. Deploy to Railway")
        print("2. Test live updates on website")
        print("3. Run price simulation: python simulate_live_updates.py --single")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
