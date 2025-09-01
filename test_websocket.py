#!/usr/bin/env python
"""
Simple WebSocket test script to verify the connection works
"""
import asyncio
import websockets
import json

async def test_websocket():
    """Test WebSocket connection to price-feeds endpoint"""
    uri = "ws://localhost:8000/ws/price-feeds/"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a test message
            test_message = {"type": "get_prices"}
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent message: {test_message}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds")
            
            print("✅ WebSocket test completed successfully!")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused. Make sure the Django server is running with ASGI support.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
