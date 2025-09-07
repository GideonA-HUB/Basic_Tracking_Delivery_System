#!/usr/bin/env python3
"""
Test WebSocket connection for delivery tracking
"""
import os
import sys
import django
import asyncio
import websockets
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from tracking.models import Delivery

async def test_websocket_connection():
    """Test WebSocket connection to delivery tracking"""
    
    # Get a test delivery
    try:
        delivery = Delivery.objects.first()
        if not delivery:
            print("❌ No deliveries found in database")
            return False
            
        print(f"📦 Testing with delivery: {delivery.tracking_number}")
        
        # WebSocket URL
        ws_url = f"wss://meridianassetlogistics.com/ws/track/{delivery.tracking_number}/{delivery.tracking_secret}/"
        print(f"🔌 Connecting to: {ws_url}")
        
        try:
            async with websockets.connect(ws_url) as websocket:
                print("✅ WebSocket connected successfully!")
                
                # Send request for tracking data
                message = {"type": "get_tracking_data"}
                await websocket.send(json.dumps(message))
                print("📤 Sent tracking data request")
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(response)
                print(f"📨 Received response: {data.get('type', 'unknown')}")
                
                if data.get('type') == 'tracking_data':
                    print("✅ Successfully received tracking data!")
                    return True
                else:
                    print(f"❌ Unexpected response type: {data.get('type')}")
                    return False
                    
        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ WebSocket connection closed: {e}")
            return False
        except asyncio.TimeoutError:
            print("❌ WebSocket connection timeout")
            return False
        except Exception as e:
            print(f"❌ WebSocket connection error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Test setup error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing WebSocket connection...")
    result = asyncio.run(test_websocket_connection())
    if result:
        print("🎉 WebSocket test passed!")
    else:
        print("💥 WebSocket test failed!")