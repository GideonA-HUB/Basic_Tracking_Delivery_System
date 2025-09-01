import requests
import json
import logging
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta
import random
from .models import RealTimePriceFeed, InvestmentItem, PriceHistory

logger = logging.getLogger(__name__)

class RealTimePriceService:
    """Service for fetching real-time prices from external APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_crypto_prices(self):
        """Fetch cryptocurrency prices from CoinGecko API"""
        try:
            # CoinGecko API for crypto prices
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum,cardano',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            prices = {}
            for coin_id, price_data in data.items():
                if coin_id == 'bitcoin':
                    symbol = 'BTC'
                elif coin_id == 'ethereum':
                    symbol = 'ETH'
                elif coin_id == 'cardano':
                    symbol = 'ADA'
                else:
                    continue
                
                prices[symbol] = {
                    'price': Decimal(str(price_data['usd'])),
                    'change_24h': Decimal(str(price_data.get('usd_24h_change', 0)))
                }
            
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return {}
    
    def fetch_gold_silver_prices(self):
        """Fetch gold and silver prices from Metals API"""
        try:
            # Metals API for precious metals
            url = "https://api.metals.live/v1/spot"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            prices = {}
            for metal in data:
                if metal['commodity'] == 'XAU' and metal['currency'] == 'USD':
                    prices['XAU'] = {
                        'price': Decimal(str(metal['price'])),
                        'change_24h': Decimal(str(metal.get('change', 0)))
                    }
                elif metal['commodity'] == 'XAG' and metal['currency'] == 'USD':
                    prices['XAG'] = {
                        'price': Decimal(str(metal['price'])),
                        'change_24h': Decimal(str(metal.get('change', 0)))
                    }
                elif metal['commodity'] == 'XPT' and metal['currency'] == 'USD':
                    prices['XPT'] = {
                        'price': Decimal(str(metal['price'])),
                        'change_24h': Decimal(str(metal.get('change', 0)))
                    }
            
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching metals prices: {e}")
            return {}
    
    def fetch_real_estate_indices(self):
        """Fetch real estate indices (simulated for now)"""
        try:
            # Simulate real estate price movements
            base_prices = {
                'REIT_INDEX': 1500.00,
                'PROPERTY_FUND': 2500.00
            }
            
            prices = {}
            for index, base_price in base_prices.items():
                # Simulate small daily changes
                change_percent = random.uniform(-2.0, 2.0)
                change_amount = base_price * (change_percent / 100)
                new_price = base_price + change_amount
                
                prices[index] = {
                    'price': Decimal(str(new_price)),
                    'change_24h': Decimal(str(change_amount))
                }
            
            return prices
            
        except Exception as e:
            logger.error(f"Error fetching real estate indices: {e}")
            return {}
    
    def update_all_prices(self):
        """Update all price feeds with real-time data"""
        try:
            # Fetch prices from all sources
            crypto_prices = self.fetch_crypto_prices()
            metals_prices = self.fetch_gold_silver_prices()
            real_estate_prices = self.fetch_real_estate_indices()
            
            # Combine all prices
            all_prices = {**crypto_prices, **metals_prices, **real_estate_prices}
            
            # Update price feeds
            updated_count = 0
            for symbol, price_data in all_prices.items():
                try:
                    feed = RealTimePriceFeed.objects.filter(symbol=symbol).first()
                    if feed:
                        old_price = feed.current_price
                        new_price = price_data['price']
                        change_amount = price_data['change_24h']
                        change_percentage = (change_amount / old_price * 100) if old_price > 0 else 0
                        
                        # Update the feed
                        feed.update_price(new_price, change_amount, change_percentage)
                        
                        # Create price history record
                        PriceHistory.objects.create(
                            real_time_price_feed=feed,
                            price=new_price,
                            change_amount=change_amount,
                            change_percentage=change_percentage,
                            timestamp=timezone.now()
                        )
                        
                        updated_count += 1
                        logger.info(f"Updated {symbol}: ${new_price} ({change_percentage:+.2f}%)")
                        
                except Exception as e:
                    logger.error(f"Error updating {symbol}: {e}")
            
            # Update investment item prices based on price feeds
            self.update_investment_item_prices()
            
            logger.info(f"Updated {updated_count} price feeds")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating all prices: {e}")
            return 0
    
    def update_investment_item_prices(self):
        """Update investment item prices based on price feeds"""
        try:
            # Map investment items to price feeds
            item_feed_mapping = {
                'Bitcoin (BTC)': 'BTC',
                'Ethereum (ETH)': 'ETH',
                'Cardano (ADA)': 'ADA',
                'Gold Bullion (1 oz)': 'XAU',
                'Silver Bullion (1 oz)': 'XAG',
                'Platinum Bullion (1 oz)': 'XPT',
            }
            
            for item_name, feed_symbol in item_feed_mapping.items():
                try:
                    item = InvestmentItem.objects.filter(name=item_name).first()
                    feed = RealTimePriceFeed.objects.filter(symbol=feed_symbol).first()
                    
                    if item and feed:
                        old_price = item.current_price_usd
                        new_price = feed.current_price
                        
                        if old_price != new_price:
                            # Calculate price change
                            price_change = new_price - old_price
                            price_change_percentage = (price_change / old_price * 100) if old_price > 0 else 0
                            
                            # Update item price
                            item.current_price_usd = new_price
                            item.price_change_24h = price_change
                            item.price_change_percentage_24h = price_change_percentage
                            item.last_price_update = timezone.now()
                            item.save()
                            
                            logger.info(f"Updated {item_name}: ${new_price} ({price_change_percentage:+.2f}%)")
                            
                except Exception as e:
                    logger.error(f"Error updating {item_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error updating investment item prices: {e}")
    
    def get_price_chart_data(self, item, days=30):
        """Get price chart data for an item"""
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # Get price history for the item's price feed
            if hasattr(item, 'price_feed') and item.price_feed:
                history = PriceHistory.objects.filter(
                    real_time_price_feed=item.price_feed,
                    timestamp__range=(start_date, end_date)
                ).order_by('timestamp')
            else:
                # Generate simulated data
                history = self.generate_simulated_price_history(item, start_date, end_date)
            
            chart_data = {
                'labels': [],
                'prices': [],
                'changes': []
            }
            
            for record in history:
                chart_data['labels'].append(record.timestamp.strftime('%Y-%m-%d'))
                chart_data['prices'].append(float(record.price))
                chart_data['changes'].append(float(record.change_percentage))
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error getting chart data: {e}")
            return {'labels': [], 'prices': [], 'changes': []}
    
    def generate_simulated_price_history(self, item, start_date, end_date):
        """Generate simulated price history for items without price feeds"""
        history = []
        base_price = float(item.current_price_usd)
        current_date = start_date
        
        while current_date <= end_date:
            # Simulate price movement
            change_percent = random.uniform(-5.0, 5.0)
            change_amount = base_price * (change_percent / 100)
            price = base_price + change_amount
            
            history.append({
                'timestamp': current_date,
                'price': Decimal(str(price)),
                'change_percentage': Decimal(str(change_percent))
            })
            
            base_price = price
            current_date += timedelta(days=1)
        
        return history


# Global instance
price_service = RealTimePriceService()


def update_real_time_prices():
    """Function to update real-time prices (can be called by Celery)"""
    return price_service.update_all_prices()


def get_live_price_updates():
    """Get live price updates for WebSocket broadcasting"""
    try:
        feeds = RealTimePriceFeed.objects.filter(is_active=True)
        updates = []
        
        for feed in feeds:
            updates.append({
                'symbol': feed.symbol,
                'name': feed.name,
                'price': float(feed.current_price),
                'change_24h': float(feed.price_change_24h),
                'change_percentage': float(feed.price_change_percentage_24h),
                'last_updated': feed.last_updated.isoformat() if feed.last_updated else None
            })
        
        return updates
        
    except Exception as e:
        logger.error(f"Error getting live price updates: {e}")
        return [] 
