import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.apps import apps

logger = logging.getLogger(__name__)

class InvestmentConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time investment updates"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'investments_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial investment data
        await self.send_investment_data()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'get_investments':
            await self.send_investment_data()
        elif message_type == 'get_portfolio':
            await self.send_portfolio_data()
    
    async def send_investment_data(self):
        """Send current investment data to client"""
        investments = await self.get_user_investments()
        await self.send(text_data=json.dumps({
            'type': 'investment_data',
            'investments': investments
        }))
    
    async def send_portfolio_data(self):
        """Send portfolio data to client"""
        portfolio = await self.get_user_portfolio()
        await self.send(text_data=json.dumps({
            'type': 'portfolio_data',
            'portfolio': portfolio
        }))
    
    @database_sync_to_async
    def get_user_investments(self):
        """Get user investments from database"""
        try:
            # Get models dynamically to avoid import issues
            User = apps.get_model('auth', 'User')
            UserInvestment = apps.get_model('investments', 'UserInvestment')
            
            user = User.objects.get(id=self.user_id)
            investments = UserInvestment.objects.filter(user=user, status='active')
            return [{
                'id': inv.id,
                'item_name': inv.item.name,
                'investment_amount': float(inv.investment_amount_usd),
                'current_value': float(inv.current_value_usd),
                'total_return': float(inv.total_return_usd),
                'total_return_percentage': float(inv.total_return_percentage),
                'purchased_at': inv.purchased_at.isoformat(),
                'status': inv.status
            } for inv in investments]
        except Exception as e:
            logger.error(f"Error getting user investments: {e}")
            return []
    
    @database_sync_to_async
    def get_user_portfolio(self):
        """Get user portfolio from database"""
        try:
            # Get models dynamically to avoid import issues
            User = apps.get_model('auth', 'User')
            InvestmentPortfolio = apps.get_model('investments', 'InvestmentPortfolio')
            
            user = User.objects.get(id=self.user_id)
            portfolio = InvestmentPortfolio.objects.get(user=user)
            return {
                'total_invested': float(portfolio.total_invested),
                'current_value': float(portfolio.current_value),
                'total_return': float(portfolio.total_return),
                'total_return_percentage': float(portfolio.total_return_percentage),
                'active_investments_count': portfolio.active_investments_count,
                'last_updated': portfolio.last_updated.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting user portfolio: {e}")
            return {}


class PriceFeedConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time price feed updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            self.room_group_name = 'price_feeds'
            logger.info(f"WebSocket connection attempt from {self.scope.get('client', ['unknown'])[0]}")
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info("WebSocket connection accepted successfully")
            
            # FORCE UPDATE PRICES FROM APIs IMMEDIATELY
            await self.force_update_prices_from_apis()
            
            # Send initial price data immediately
            await self.send_price_data()
            
            # Start periodic updates every 30 seconds
            await self.start_periodic_updates()
            
        except Exception as e:
            logger.error(f"Error in WebSocket connect: {e}")
            if hasattr(self, 'channel_name'):
                await self.close()
    
    @database_sync_to_async
    def force_update_prices_from_apis(self):
        """Force update prices from APIs with graceful error handling"""
        try:
            logger.info("🔄 FORCING PRICE UPDATE FROM APIs...")
            
            # Try to import and use price service, but handle failures gracefully
            try:
                from investments.price_services import price_service
                updated_count = price_service.update_all_prices()
                logger.info(f"✅ Updated {updated_count} prices from APIs successfully")
            except Exception as api_error:
                logger.warning(f"API price update failed: {api_error}")
                # Continue with existing data instead of failing completely
                updated_count = 0
            
            # Log current major prices (even if API update failed)
            major_cryptos = ['BTC', 'ETH', 'ADA', 'SOL']
            logger.info("💰 Current prices in database:")
            for symbol in major_cryptos:
                try:
                    from investments.models import RealTimePriceFeed
                    feed = RealTimePriceFeed.objects.filter(symbol=symbol).first()
                    if feed:
                        logger.info(f"   {feed.name}: ${feed.current_price:,.2f} ({feed.price_change_percentage_24h:+.2f}%)")
                except Exception as e:
                    logger.warning(f"Could not log price for {symbol}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Price update process failed: {e}")
            # Return True to continue with existing data rather than failing completely
            return True
    
    async def start_periodic_updates(self):
        """Start periodic price updates every 5 minutes to avoid rate limits"""
        import asyncio
        
        async def periodic_update():
            while True:
                try:
                    await asyncio.sleep(300)  # Wait 5 minutes to avoid rate limits
                    logger.info("🔄 Running periodic price update...")
                    
                    # Force update prices from APIs (with error handling)
                    try:
                        await self.force_update_prices_from_apis()
                    except Exception as update_error:
                        logger.warning(f"Periodic price update failed: {update_error}")
                        # Continue to send existing data
                    
                    # Send updated price data (even if update failed)
                    try:
                        await self.send_price_data()
                    except Exception as send_error:
                        logger.warning(f"Failed to send price data: {send_error}")
                    
                except Exception as e:
                    logger.error(f"Error in periodic update: {e}")
                    # Don't break the loop, just continue
                    await asyncio.sleep(300)  # Wait before retrying
        
        # Start the periodic update task
        asyncio.create_task(periodic_update())
        logger.info("✅ Periodic updates started (every 5 minutes)")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection with proper cleanup"""
        try:
            logger.info(f"WebSocket disconnected with code: {close_code}")
            
            # Cancel any running tasks to prevent hanging
            if hasattr(self, '_periodic_task') and self._periodic_task:
                self._periodic_task.cancel()
                try:
                    await self._periodic_task
                except asyncio.CancelledError:
                    logger.info("Periodic update task cancelled successfully")
            
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            logger.info("WebSocket cleanup completed successfully")
        except Exception as e:
            logger.error(f"Error in WebSocket disconnect: {e}")
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            logger.info(f"Received WebSocket message: {text_data}")
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'get_prices':
                logger.info("Client requested price data")
                # Force update prices from APIs before sending
                await self.force_update_prices_from_apis()
                await self.send_price_data()
            elif message_type == 'force_update':
                logger.info("Client requested force price update")
                # Force update prices from APIs
                await self.force_update_prices_from_apis()
                await self.send_price_data()
            else:
                logger.info(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def send_price_data(self):
        """Send current price data to client with movement statistics"""
        try:
            logger.info("Fetching price data from database...")
            
            # Get price data using sync_to_async
            price_data = await self.get_price_data()
            
            # Calculate movement statistics
            increases = 0
            decreases = 0
            unchanged = 0
            
            for price in price_data:
                change = price.get('price_change_percentage_24h', 0)
                if change > 0:
                    increases += 1
                elif change < 0:
                    decreases += 1
                else:
                    unchanged += 1
            
            movement_stats = {
                'increases': increases,
                'decreases': decreases,
                'unchanged': unchanged,
                'total': increases + decreases
            }
            
            response_data = {
                'type': 'price_data',
                'prices': price_data,
                'movement_stats': movement_stats,
                'update_count': len(price_data),
                'timestamp': await self.get_current_timestamp(),
                'total_items': len(price_data)
            }
            
            logger.info(f"Sending price data: {len(price_data)} items")
            logger.info(f"Movement stats: {increases} increases, {decreases} decreases, {unchanged} unchanged")
            await self.send(text_data=json.dumps(response_data))
            logger.info("Price data sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending price data: {e}")
            error_response = {
                'type': 'error',
                'message': f'Failed to load price data: {str(e)}'
            }
            await self.send(text_data=json.dumps(error_response))
    
    @database_sync_to_async
    def get_price_data(self):
        """Get price data from database - wrapped in sync_to_async"""
        try:
            # Get models dynamically to avoid import issues
            RealTimePriceFeed = apps.get_model('investments', 'RealTimePriceFeed')
            InvestmentItem = apps.get_model('investments', 'InvestmentItem')
            
            # Get all active price feeds
            feeds = RealTimePriceFeed.objects.filter(is_active=True)
            logger.info(f"Found {feeds.count()} active price feeds")
            
            # Get all active investment items
            items = InvestmentItem.objects.filter(is_active=True)
            logger.info(f"Found {items.count()} active investment items")
            
            price_data = []
            
            # First, add price feeds data
            for feed in feeds:
                price_data.append({
                    'symbol': feed.symbol,
                    'name': feed.name,
                    'current_price': float(feed.current_price),
                    'price_change_24h': float(feed.price_change_24h),
                    'price_change_percentage_24h': float(feed.price_change_percentage_24h),
                    'last_updated': feed.last_updated.isoformat() if feed.last_updated else None,
                    'source': 'price_feed'
                })
                logger.info(f"Added price feed data for {feed.name}: ${feed.current_price}")
            
            # Then, add investment items data (these are the actual items users can invest in)
            for item in items:
                # Try to find matching price feed
                matching_feed = None
                for feed in feeds:
                    # Check if names match (e.g., "Bitcoin (BTC)" matches "Bitcoin (BTC)")
                    if feed.name == item.name:
                        matching_feed = feed
                        break
                    # Check if symbols match (e.g., "BTC" matches "BTC")
                    elif feed.symbol and item.symbol and feed.symbol == item.symbol:
                        matching_feed = feed
                        break
                
                if matching_feed:
                    # Use price feed data for real-time updates
                    price_data.append({
                        'symbol': item.symbol or matching_feed.symbol,
                        'name': item.name,
                        'current_price': float(matching_feed.current_price),
                        'price_change_24h': float(matching_feed.price_change_24h),
                        'price_change_percentage_24h': float(matching_feed.price_change_percentage_24h),
                        'last_updated': matching_feed.last_updated.isoformat() if matching_feed.last_updated else None,
                        'source': 'investment_item',
                        'item_id': item.id,
                        'minimum_investment': float(item.minimum_investment) if item.minimum_investment else None,
                        'investment_type': item.investment_type
                    })
                    logger.info(f"Added investment item data for {item.name}: ${matching_feed.current_price}")
                else:
                    # Use item's own price data if no matching feed
                    price_data.append({
                        'symbol': item.symbol,
                        'name': item.name,
                        'current_price': float(item.current_price_usd),
                        'price_change_24h': float(item.price_change_24h) if item.price_change_24h else 0,
                        'price_change_percentage_24h': float(item.price_change_percentage_24h) if item.price_change_percentage_24h else 0,
                        'last_updated': getattr(item, 'last_price_update', item.updated_at).isoformat() if hasattr(item, 'last_price_update') and item.last_price_update else item.updated_at.isoformat(),
                        'source': 'investment_item_static',
                        'item_id': item.id,
                        'minimum_investment': float(item.minimum_investment) if item.minimum_investment else None,
                        'investment_type': item.investment_type
                    })
                    logger.info(f"Added static investment item data for {item.name}: ${item.current_price_usd}")
            
            return price_data
            
        except Exception as e:
            logger.error(f"Error getting price data: {e}")
            return []
    
    @database_sync_to_async
    def get_current_timestamp(self):
        """Get current timestamp - wrapped in sync_to_async"""
        from django.utils import timezone
        return timezone.now().isoformat()
    
    async def price_update(self, event):
        """Handle price update events from channel layer"""
        try:
            logger.info(f"Broadcasting price update to {self.channel_name}")
            
            # Enhanced price update with movement stats
            update_data = {
                'type': 'price_update',
                'price_data': event.get('price_data', []),
                'movement_stats': event.get('movement_stats', {}),
                'update_count': event.get('update_count', 0),
                'timestamp': timezone.now().isoformat(),
                'total_items': len(event.get('price_data', []))
            }
            
            await self.send(text_data=json.dumps(update_data))
            logger.info(f"Successfully broadcasted enhanced price update with {len(update_data['price_data'])} items")
        except Exception as e:
            logger.error(f"Error broadcasting price update: {e}")
    
    async def portfolio_update(self, event):
        """Handle portfolio update events"""
        try:
            logger.info(f"Broadcasting portfolio update to {self.channel_name}")
            await self.send(text_data=json.dumps({
                'type': 'portfolio_update',
                'portfolio_data': event['portfolio_data'],
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error broadcasting portfolio update: {e}")
    
    @classmethod
    async def broadcast_price_update(cls, price_data):
        """Broadcast price update to all connected clients"""
        try:
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                'price_feeds',
                {
                    'type': 'price_update',
                    'price_data': price_data
                }
            )
            logger.info("Price update broadcasted successfully")
        except Exception as e:
            logger.error(f"Error broadcasting price update: {e}")


class PortfolioConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time portfolio updates"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'portfolio_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial portfolio data
        await self.send_portfolio_data()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'get_portfolio':
            await self.send_portfolio_data()
    
    async def send_portfolio_data(self):
        """Send portfolio data to client"""
        try:
            # Get portfolio data using sync_to_async
            portfolio_data = await self.get_portfolio_data()
            
            await self.send(text_data=json.dumps({
                'type': 'portfolio_data',
                'portfolio': portfolio_data
            }))
        except Exception as e:
            logger.error(f"Error sending portfolio data: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to load portfolio data'
            }))
    
    @database_sync_to_async
    def get_portfolio_data(self):
        """Get portfolio data from database - wrapped in sync_to_async"""
        try:
            # Get models dynamically to avoid import issues
            User = apps.get_model('auth', 'User')
            InvestmentPortfolio = apps.get_model('investments', 'InvestmentPortfolio')
            
            user = User.objects.get(id=self.user_id)
            portfolio = InvestmentPortfolio.objects.get(user=user)
            
            return {
                'total_invested': float(portfolio.total_invested),
                'current_value': float(portfolio.current_value),
                'total_return': float(portfolio.total_return),
                'total_return_percentage': float(portfolio.total_return_percentage),
                'active_investments_count': portfolio.active_investments_count,
                'last_updated': portfolio.last_updated.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting portfolio data: {e}")
            return {}
