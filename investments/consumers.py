import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.apps import apps


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
            return {}


class PriceFeedConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time price feed updates"""
    
    async def connect(self):
        self.room_group_name = 'price_feeds'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial price data
        await self.send_price_data()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'get_prices':
                await self.send_price_data()
        except json.JSONDecodeError:
            pass
    
    async def send_price_data(self):
        """Send current price data to client"""
        try:
            # Get models dynamically to avoid import issues
            RealTimePriceFeed = apps.get_model('investments', 'RealTimePriceFeed')
            
            feeds = RealTimePriceFeed.objects.filter(is_active=True)
            price_data = []
            
            for feed in feeds:
                price_data.append({
                    'symbol': feed.symbol,
                    'name': feed.name,
                    'current_price': float(feed.current_price),
                    'price_change_24h': float(feed.price_change_24h),
                    'price_change_percentage_24h': float(feed.price_change_percentage_24h),
                    'last_updated': feed.last_updated.isoformat() if feed.last_updated else None
                })
            
            await self.send(text_data=json.dumps({
                'type': 'price_data',
                'prices': price_data
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to load price data'
            }))
    
    async def price_update(self, event):
        """Handle price update events"""
        await self.send(text_data=json.dumps({
            'type': 'price_update',
            'price_data': event['price_data']
        }))
    
    @classmethod
    async def broadcast_price_update(cls, price_data):
        """Broadcast price update to all connected clients"""
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            'price_feeds',
            {
                'type': 'price_update',
                'price_data': price_data
            }
        )


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
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to load portfolio data'
            }))
