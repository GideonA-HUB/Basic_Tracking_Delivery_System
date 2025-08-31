import requests
import asyncio
import aiohttp
from decimal import Decimal
from django.utils import timezone
from .models import RealTimePriceFeed, RealTimePriceHistory


class PriceFeedService:
    """Service for fetching and updating real-time price feeds"""
    
    # API endpoints for different asset types
    API_ENDPOINTS = {
        'gold': {
            'url': 'https://api.metals.live/v1/spot/gold',
            'parser': 'metals_live'
        },
        'silver': {
            'url': 'https://api.metals.live/v1/spot/silver',
            'parser': 'metals_live'
        },
        'crypto': {
            'url': 'https://api.coingecko.com/api/v3/simple/price',
            'parser': 'coingecko'
        },
        'real_estate': {
            'url': 'https://api.example.com/real-estate',  # Placeholder
            'parser': 'custom'
        }
    }
    
    @classmethod
    async def update_all_price_feeds(cls):
        """Update all active price feeds asynchronously"""
        active_feeds = RealTimePriceFeed.objects.filter(is_active=True)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for feed in active_feeds:
                task = cls.update_price_feed(session, feed)
                tasks.append(task)
            
            # Execute all updates concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and log any errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Error updating price feed {active_feeds[i].name}: {result}")
        
        return True
    
    @classmethod
    async def update_price_feed(cls, session, price_feed):
        """Update a specific price feed"""
        try:
            if price_feed.asset_type in ['gold', 'silver']:
                await cls.update_metal_prices(session, price_feed)
            elif price_feed.asset_type == 'crypto':
                await cls.update_crypto_prices(session, price_feed)
            elif price_feed.asset_type == 'real_estate':
                await cls.update_real_estate_prices(session, price_feed)
            else:
                await cls.update_custom_prices(session, price_feed)
                
        except Exception as e:
            print(f"Error updating {price_feed.name}: {e}")
            raise
    
    @classmethod
    async def update_metal_prices(cls, session, price_feed):
        """Update precious metal prices"""
        try:
            # Use metals.live API for precious metals
            url = "https://api.metals.live/v1/spot"
            params = {'metals': price_feed.symbol.lower() if price_feed.symbol else price_feed.asset_type}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data and len(data) > 0:
                        metal_data = data[0]
                        new_price = Decimal(str(metal_data.get('price', 0)))
                        
                        # Calculate price changes
                        old_price = price_feed.current_price
                        price_change = new_price - old_price
                        price_change_percentage = (price_change / old_price * 100) if old_price > 0 else 0
                        
                        # Update the price feed
                        price_feed.update_price(
                            new_price=new_price,
                            price_change_24h=price_change,
                            price_change_percentage_24h=price_change_percentage
                        )
                        
                        print(f"Updated {price_feed.name}: ${new_price} ({price_change_percentage:+.2f}%)")
                        
        except Exception as e:
            print(f"Error updating metal prices for {price_feed.name}: {e}")
            raise
    
    @classmethod
    async def update_crypto_prices(cls, session, price_feed):
        """Update cryptocurrency prices"""
        try:
            # Use CoinGecko API for crypto prices
            symbol = price_feed.symbol.lower() if price_feed.symbol else 'bitcoin'
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': symbol,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_7d_change': 'true'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if symbol in data:
                        crypto_data = data[symbol]
                        new_price = Decimal(str(crypto_data.get('usd', 0)))
                        price_change_24h = Decimal(str(crypto_data.get('usd_24h_change', 0)))
                        
                        # Update the price feed
                        price_feed.update_price(
                            new_price=new_price,
                            price_change_24h=price_change_24h,
                            price_change_percentage_24h=price_change_24h
                        )
                        
                        print(f"Updated {price_feed.name}: ${new_price} ({price_change_24h:+.2f}%)")
                        
        except Exception as e:
            print(f"Error updating crypto prices for {price_feed.name}: {e}")
            raise
    
    @classmethod
    async def update_real_estate_prices(cls, session, price_feed):
        """Update real estate prices (placeholder implementation)"""
        try:
            # This would integrate with real estate APIs
            # For now, we'll use a simulated update
            current_price = price_feed.current_price
            # Simulate small random price movement
            import random
            change_percentage = Decimal(str(random.uniform(-2.0, 2.0)))
            new_price = current_price * (1 + change_percentage / 100)
            price_change = new_price - current_price
            
            price_feed.update_price(
                new_price=new_price,
                price_change_24h=price_change,
                price_change_percentage_24h=change_percentage
            )
            
            print(f"Updated {price_feed.name}: ${new_price} ({change_percentage:+.2f}%)")
            
        except Exception as e:
            print(f"Error updating real estate prices for {price_feed.name}: {e}")
            raise
    
    @classmethod
    async def update_custom_prices(cls, session, price_feed):
        """Update custom asset prices"""
        try:
            # For custom assets, we might have specific APIs
            # This is a placeholder for future implementations
            print(f"Custom price update not implemented for {price_feed.name}")
            
        except Exception as e:
            print(f"Error updating custom prices for {price_feed.name}: {e}")
            raise
    
    @classmethod
    def create_sample_price_feeds(cls):
        """Create sample price feeds for testing"""
        sample_feeds = [
            {
                'name': 'Gold (XAU)',
                'asset_type': 'gold',
                'symbol': 'XAU',
                'current_price': Decimal('1950.00'),
                'base_currency': 'USD'
            },
            {
                'name': 'Silver (XAG)',
                'asset_type': 'silver',
                'symbol': 'XAG',
                'current_price': Decimal('24.50'),
                'base_currency': 'USD'
            },
            {
                'name': 'Bitcoin (BTC)',
                'asset_type': 'crypto',
                'symbol': 'BTC',
                'current_price': Decimal('45000.00'),
                'base_currency': 'USD'
            },
            {
                'name': 'Ethereum (ETH)',
                'asset_type': 'crypto',
                'symbol': 'ETH',
                'current_price': Decimal('2800.00'),
                'base_currency': 'USD'
            },
            {
                'name': 'Platinum (XPT)',
                'asset_type': 'platinum',
                'symbol': 'XPT',
                'current_price': Decimal('950.00'),
                'base_currency': 'USD'
            },
            {
                'name': 'Palladium (XPD)',
                'asset_type': 'palladium',
                'symbol': 'XPD',
                'current_price': Decimal('1200.00'),
                'base_currency': 'USD'
            }
        ]
        
        created_feeds = []
        for feed_data in sample_feeds:
            feed, created = RealTimePriceFeed.objects.get_or_create(
                name=feed_data['name'],
                defaults=feed_data
            )
            if created:
                created_feeds.append(feed)
                print(f"Created price feed: {feed.name}")
        
        return created_feeds


class CurrencyConversionService:
    """Service for currency conversion"""
    
    @classmethod
    async def update_exchange_rates(cls):
        """Update currency exchange rates"""
        try:
            # Use a free currency API
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Update exchange rates in database
                        from .models import CurrencyConversion
                        
                        base_currency = 'USD'
                        rates = data.get('rates', {})
                        
                        for currency, rate in rates.items():
                            if currency != base_currency:
                                conversion, created = CurrencyConversion.objects.get_or_create(
                                    from_currency=base_currency,
                                    to_currency=currency,
                                    defaults={'exchange_rate': Decimal(str(rate))}
                                )
                                
                                if not created:
                                    conversion.exchange_rate = Decimal(str(rate))
                                    conversion.save()
                        
                        print(f"Updated {len(rates)} exchange rates")
                        return True
                        
        except Exception as e:
            print(f"Error updating exchange rates: {e}")
            return False
    
    @classmethod
    def convert_currency(cls, amount, from_currency, to_currency):
        """Convert amount between currencies"""
        from .models import CurrencyConversion
        
        if from_currency == to_currency:
            return amount
        
        try:
            conversion = CurrencyConversion.get_conversion_rate(from_currency, to_currency)
            if conversion:
                return amount * conversion
            else:
                print(f"No conversion rate found for {from_currency} to {to_currency}")
                return amount
        except Exception as e:
            print(f"Error converting currency: {e}")
            return amount 
