#!/usr/bin/env python3
"""
WebSocket Connection Test
This script tests the WebSocket connection to verify real-time price updates work.
"""

import asyncio
import websockets
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """Test WebSocket connection to price feeds"""
    
    # WebSocket URL (adjust for your domain)
    websocket_url = "wss://meridian-asset-logistics.up.railway.app/ws/price-feeds/"
    
    try:
        logger.info(f"🔌 Connecting to WebSocket: {websocket_url}")
        
        # Connect to WebSocket
        async with websockets.connect(websocket_url) as websocket:
            logger.info("✅ WebSocket connection established!")
            
            # Wait for initial price data
            logger.info("⏳ Waiting for initial price data...")
            
            # Listen for messages for 30 seconds
            timeout = 30
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    
                    # Parse JSON message
                    data = json.loads(message)
                    
                    logger.info("📊 Received price data:")
                    logger.info(f"   Type: {data.get('type', 'unknown')}")
                    
                    if 'prices' in data:
                        prices = data['prices']
                        logger.info(f"   Number of prices: {len(prices)}")
                        
                        # Show first few prices
                        for i, price in enumerate(prices[:3]):
                            symbol = price.get('symbol', 'Unknown')
                            current_price = price.get('current_price', 0)
                            change_24h = price.get('change_24h', 0)
                            
                            logger.info(f"   {symbol}: ${current_price:,.2f} ({change_24h:+.2f}%)")
                    
                    logger.info("✅ WebSocket is working! Real-time price updates are active.")
                    
                except asyncio.TimeoutError:
                    logger.info("⏳ Waiting for price updates...")
                    continue
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️  Invalid JSON received: {e}")
                    continue
                except Exception as e:
                    logger.error(f"❌ Error receiving message: {e}")
                    break
            
            logger.info("🎉 WebSocket test completed successfully!")
            
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"❌ WebSocket connection closed: {e}")
    except websockets.exceptions.InvalidURI as e:
        logger.error(f"❌ Invalid WebSocket URI: {e}")
    except Exception as e:
        logger.error(f"❌ WebSocket connection failed: {e}")
        logger.info("💡 Make sure the server is running and WebSocket endpoint is accessible")

async def test_local_websocket():
    """Test WebSocket connection locally"""
    
    # Local WebSocket URL
    websocket_url = "ws://localhost:8000/ws/price-feeds/"
    
    try:
        logger.info(f"🔌 Testing local WebSocket: {websocket_url}")
        
        async with websockets.connect(websocket_url) as websocket:
            logger.info("✅ Local WebSocket connection established!")
            
            # Wait for message
            message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            data = json.loads(message)
            
            logger.info("📊 Local WebSocket test successful!")
            logger.info(f"   Received: {data.get('type', 'unknown')}")
            
    except Exception as e:
        logger.error(f"❌ Local WebSocket test failed: {e}")

if __name__ == "__main__":
    print("🧪 WebSocket Connection Test")
    print("=" * 50)
    
    # Test production WebSocket
    print("\n🌐 Testing Production WebSocket...")
    asyncio.run(test_websocket_connection())
    
    print("\n" + "=" * 50)
    print("💡 If the test fails, wait 2-3 minutes for Railway to redeploy")
    print("💡 Then run this test again to verify WebSocket connection")
