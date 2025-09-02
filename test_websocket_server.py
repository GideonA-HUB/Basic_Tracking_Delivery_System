#!/usr/bin/env python
"""
Test script to verify WebSocket server functionality
"""
import os
import sys
import django
import asyncio
import json
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.test import override_settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')

# Initialize Django
django.setup()

from delivery_tracker.asgi import application
from investments.routing import websocket_urlpatterns

async def test_websocket():
    """Test WebSocket connection and data flow"""
    print("🧪 Testing WebSocket Server...")
    
    try:
        # Create a test communicator
        communicator = WebsocketCommunicator(
            application,
            "/ws/price-feeds/"
        )
        
        # Connect to WebSocket
        print("📡 Connecting to WebSocket...")
        connected, _ = await communicator.connect()
        
        if connected:
            print("✅ WebSocket connected successfully!")
            
            # Test sending a message
            print("📤 Sending 'get_prices' message...")
            await communicator.send_json_to({
                "type": "get_prices"
            })
            
            # Wait for response
            print("⏳ Waiting for response...")
            response = await communicator.receive_json_from()
            
            print(f"📥 Received response: {json.dumps(response, indent=2)}")
            
            if response.get('type') == 'price_data':
                prices = response.get('prices', [])
                print(f"✅ Received {len(prices)} price items:")
                for price in prices[:3]:  # Show first 3
                    print(f"  - {price['name']}: ${price['current_price']}")
            else:
                print(f"❌ Unexpected response type: {response.get('type')}")
            
            # Close connection
            await communicator.disconnect()
            print("🔌 WebSocket disconnected")
            
        else:
            print("❌ Failed to connect to WebSocket")
            
    except Exception as e:
        print(f"❌ Error testing WebSocket: {e}")
        import traceback
        traceback.print_exc()

async def test_price_feeds():
    """Test if price feeds exist and have data"""
    print("\n🔍 Testing Price Feeds...")
    
    try:
        from investments.models import RealTimePriceFeed
        
        feeds = RealTimePriceFeed.objects.filter(is_active=True)
        print(f"📊 Found {feeds.count()} active price feeds:")
        
        for feed in feeds:
            print(f"  - {feed.name} ({feed.symbol}): ${feed.current_price}")
            
        if feeds.count() > 0:
            print("✅ Price feeds are available")
        else:
            print("❌ No price feeds found!")
            
    except Exception as e:
        print(f"❌ Error checking price feeds: {e}")

async def main():
    """Main test function"""
    print("🚀 WebSocket Server Test")
    print("=" * 50)
    
    await test_price_feeds()
    await test_websocket()
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
