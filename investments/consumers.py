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
            
            # Send initial price data immediately
            await self.send_price_data()
            
        except Exception as e:
            logger.error(f"Error in WebSocket connect: {e}")
            if hasattr(self, 'channel_name'):
                await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            logger.info(f"WebSocket disconnected with code: {close_code}")
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
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
        """Send current price data to client"""
        try:
            logger.info("Fetching price data from database...")
            
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
                        'last_updated': item.last_price_update.isoformat() if item.last_price_update else None,
                        'source': 'investment_item_static',
                        'item_id': item.id,
                        'minimum_investment': float(item.minimum_investment) if item.minimum_investment else None,
                        'investment_type': item.investment_type
                    })
                    logger.info(f"Added static investment item data for {item.name}: ${item.current_price_usd}")
            
            response_data = {
                'type': 'price_data',
                'prices': price_data,
                'timestamp': apps.get_model('django.utils', 'timezone').now().isoformat(),
                'total_items': len(price_data)
            }
            
            logger.info(f"Sending price data: {len(price_data)} items")
            await self.send(text_data=json.dumps(response_data))
            logger.info("Price data sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending price data: {e}")
            error_response = {
                'type': 'error',
                'message': f'Failed to load price data: {str(e)}'
            }
            await self.send(text_data=json.dumps(error_response))
    
    async def price_update(self, event):
        """Handle price update events from channel layer"""
        try:
            logger.info(f"Broadcasting price update: {event}")
            await self.send(text_data=json.dumps({
                'type': 'price_update',
                'price_data': event['price_data']
            }))
        except Exception as e:
            logger.error(f"Error broadcasting price update: {e}")
    
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
            # Get models dynamically to avoid import issues
            User = apps.get_model('auth', 'User')
            InvestmentPortfolio = apps.get_model('investments', 'InvestmentPortfolio')
            
            user = User.objects.get(id=self.user_id)
            portfolio = InvestmentPortfolio.objects.get(user=user)
            
            await self.send(text_data=json.dumps({
                'type': 'portfolio_data',
                'portfolio': {
                    'total_invested': float(portfolio.total_invested),
                    'current_value': float(portfolio.current_value),
                    'total_return': float(portfolio.total_return),
                    'total_return_percentage': float(portfolio.total_return_percentage),
                    'active_investments_count': portfolio.active_investments_count,
                    'last_updated': portfolio.last_updated.isoformat()
                }
            }))
        except Exception as e:
            logger.error(f"Error sending portfolio data: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to load portfolio data'
            }))
