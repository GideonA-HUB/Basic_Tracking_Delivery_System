"""
Simple WebSocket consumers that don't require Redis
"""
import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)

class SimplePriceFeedConsumer(AsyncWebsocketConsumer):
    """Simple WebSocket consumer for real-time price feed updates (no Redis required)"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            logger.info(f"Simple WebSocket connection attempt from {self.scope.get('client', ['unknown'])[0]}")
            
            # Accept connection immediately
            await self.accept()
            logger.info("✅ Simple WebSocket connection accepted successfully")
            
            # Send initial price data immediately
            await self.send_initial_prices()
            
            # Start periodic updates
            await self.start_simple_periodic_updates()
            
        except Exception as e:
            logger.error(f"Error in simple WebSocket connect: {e}")
            try:
                await self.close()
            except:
                pass
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        logger.info(f"Simple WebSocket disconnected with code: {close_code}")
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
            logger.info(f"Received WebSocket message: {data}")
            
            if data.get('type') == 'get_prices':
                await self.send_current_prices()
            elif data.get('type') == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong', 'timestamp': timezone.now().isoformat()}))
                
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    async def send_initial_prices(self):
        """Send initial price data"""
        try:
            prices = await self.get_current_prices()
            await self.send(text_data=json.dumps({
                'type': 'price_update',
                'prices': prices,
                'timestamp': timezone.now().isoformat()
            }))
            logger.info("✅ Initial prices sent successfully")
        except Exception as e:
            logger.error(f"Error sending initial prices: {e}")
    
    async def send_current_prices(self):
        """Send current price data"""
        try:
            prices = await self.get_current_prices()
            await self.send(text_data=json.dumps({
                'type': 'price_update',
                'prices': prices,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending current prices: {e}")
    
    @sync_to_async
    def get_current_prices(self):
        """Get current prices from database or emergency service"""
        try:
            from .models import InvestmentItem, RealTimePriceFeed
            from .emergency_price_service import emergency_price_service
            
            prices = []
            
            # First, try to update prices using emergency service
            try:
                emergency_price_service.update_database_prices()
            except Exception as e:
                logger.warning(f"Emergency price update failed: {e}")
            
            # Get prices from RealTimePriceFeed if available
            try:
                feeds = RealTimePriceFeed.objects.filter(is_active=True)[:10]
                for feed in feeds:
                    prices.append({
                        'symbol': feed.symbol,
                        'name': feed.name,
                        'price': float(feed.current_price),
                        'change_24h': float(feed.price_change_24h),
                        'change_percentage': float(feed.price_change_percentage_24h),
                        'last_updated': feed.last_updated.isoformat() if feed.last_updated else None,
                        'source': 'price_feed'
                    })
            except Exception as e:
                logger.warning(f"Error getting price feeds: {e}")
            
            # If no price feeds, get from investment items
            if not prices:
                try:
                    items = InvestmentItem.objects.filter(is_active=True)[:10]
                    for item in items:
                        prices.append({
                            'symbol': item.symbol,
                            'name': item.name,
                            'price': float(item.current_price_usd),
                            'change_24h': float(item.price_change_24h),
                            'change_percentage': float(item.price_change_percentage_24h),
                            'last_updated': item.last_price_update.isoformat() if item.last_price_update else None,
                            'source': 'investment_item'
                        })
                except Exception as e:
                    logger.warning(f"Error getting investment items: {e}")
            
            # If still no prices, use emergency service
            if not prices:
                try:
                    prices = emergency_price_service.get_emergency_prices()
                except Exception as e:
                    logger.warning(f"Emergency service failed: {e}")
                    # Fallback to hardcoded prices
                    prices = [
                        {
                            'symbol': 'BTC',
                            'name': 'Bitcoin',
                            'price': 45000.0,
                            'change_24h': 500.0,
                            'change_percentage': 1.12,
                            'last_updated': timezone.now().isoformat(),
                            'source': 'fallback'
                        },
                        {
                            'symbol': 'ETH',
                            'name': 'Ethereum',
                            'price': 3200.0,
                            'change_24h': -50.0,
                            'change_percentage': -1.54,
                            'last_updated': timezone.now().isoformat(),
                            'source': 'fallback'
                        }
                    ]
            
            return prices
            
        except Exception as e:
            logger.error(f"Error getting current prices: {e}")
            return []
    
    async def start_simple_periodic_updates(self):
        """Start simple periodic price updates"""
        async def periodic_update():
            while True:
                try:
                    await asyncio.sleep(30)  # Update every 30 seconds
                    await self.send_current_prices()
                except Exception as e:
                    logger.error(f"Error in periodic update: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
        
        # Start the periodic update task
        asyncio.create_task(periodic_update())
        logger.info("✅ Simple periodic updates started (every 30 seconds)")
