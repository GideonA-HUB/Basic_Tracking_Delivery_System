from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from investments.models import (
    InvestmentCategory, InvestmentItem, RealTimePriceFeed, 
    CurrencyConversion, AutoInvestmentPlan
)
from decimal import Decimal


class Command(BaseCommand):
    help = 'Set up sample investment data including categories, items, and price feeds'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up sample investment data...')
        
        # Create investment categories
        categories = self.create_categories()
        self.stdout.write(f'Created {len(categories)} investment categories')
        
        # Create investment items
        items = self.create_investment_items(categories)
        self.stdout.write(f'Created {len(items)} investment items')
        
        # Create price feeds
        feeds = self.create_price_feeds()
        self.stdout.write(f'Created {len(feeds)} price feeds')
        
        # Create currency conversions
        conversions = self.create_currency_conversions()
        self.stdout.write(f'Created {len(conversions)} currency conversions')
        
        self.stdout.write(self.style.SUCCESS('Sample investment data setup completed successfully!'))
    
    def create_categories(self):
        """Create investment categories"""
        categories_data = [
            {
                'name': 'Precious Metals',
                'description': 'Gold, silver, platinum, and palladium investments',
                'icon': 'fas fa-coins',
                'color': '#FFD700'
            },
            {
                'name': 'Cryptocurrencies',
                'description': 'Digital assets like Bitcoin, Ethereum, and others',
                'icon': 'fas fa-bitcoin',
                'color': '#F7931E'
            },
            {
                'name': 'Real Estate',
                'description': 'Property investments and real estate funds',
                'icon': 'fas fa-building',
                'color': '#4A90E2'
            },
            {
                'name': 'Diamonds & Gems',
                'description': 'Precious stones and jewelry investments',
                'icon': 'fas fa-gem',
                'color': '#E91E63'
            },
            {
                'name': 'Art & Collectibles',
                'description': 'Fine art, antiques, and collectible items',
                'icon': 'fas fa-palette',
                'color': '#9C27B0'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = InvestmentCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories.append(category)
        
        return categories
    
    def create_investment_items(self, categories):
        """Create investment items"""
        items_data = [
            {
                'category': categories[0],  # Precious Metals
                'name': 'Gold Bullion (1 oz)',
                'description': 'Investment-grade gold bullion, 99.99% pure',
                'short_description': 'Pure gold bullion for investment',
                'current_price_usd': Decimal('1950.00'),
                'minimum_investment': Decimal('100.00'),
                'investment_type': 'both',
                'weight': Decimal('31.1035'),
                'purity': '99.99%',
                'is_featured': True
            },
            {
                'category': categories[0],  # Precious Metals
                'name': 'Silver Bullion (1 oz)',
                'description': 'Investment-grade silver bullion, 99.9% pure',
                'short_description': 'Pure silver bullion for investment',
                'current_price_usd': Decimal('24.50'),
                'minimum_investment': Decimal('50.00'),
                'investment_type': 'both',
                'weight': Decimal('31.1035'),
                'purity': '99.9%',
                'is_featured': True
            },
            {
                'category': categories[1],  # Cryptocurrencies
                'name': 'Bitcoin (BTC)',
                'description': 'The world\'s first decentralized cryptocurrency',
                'short_description': 'Digital gold - Bitcoin investment',
                'current_price_usd': Decimal('45000.00'),
                'minimum_investment': Decimal('100.00'),
                'investment_type': 'investment_only',
                'is_featured': True
            },
            {
                'category': categories[1],  # Cryptocurrencies
                'name': 'Ethereum (ETH)',
                'description': 'Smart contract platform and cryptocurrency',
                'short_description': 'Smart contract platform token',
                'current_price_usd': Decimal('2800.00'),
                'minimum_investment': Decimal('100.00'),
                'investment_type': 'investment_only',
                'is_featured': True
            },
            {
                'category': categories[2],  # Real Estate
                'name': 'Commercial Property Fund',
                'description': 'Diversified commercial real estate investment fund',
                'short_description': 'Commercial real estate portfolio',
                'current_price_usd': Decimal('100.00'),
                'minimum_investment': Decimal('1000.00'),
                'investment_type': 'investment_only',
                'is_featured': False
            },
            {
                'category': categories[3],  # Diamonds & Gems
                'name': 'Investment Diamond (1 carat)',
                'description': 'High-quality investment diamond, VS1 clarity, D color',
                'short_description': 'Premium investment diamond',
                'current_price_usd': Decimal('8000.00'),
                'minimum_investment': Decimal('1000.00'),
                'investment_type': 'both',
                'weight': Decimal('0.2'),
                'purity': 'VS1, D Color',
                'is_featured': True
            }
        ]
        
        items = []
        for item_data in items_data:
            item, created = InvestmentItem.objects.get_or_create(
                name=item_data['name'],
                defaults=item_data
            )
            items.append(item)
        
        return items
    
    def create_price_feeds(self):
        """Create real-time price feeds"""
        feeds_data = [
            {
                'name': 'Gold (XAU)',
                'asset_type': 'gold',
                'symbol': 'XAU',
                'current_price': Decimal('1950.00'),
                'base_currency': 'USD',
                'price_change_24h': Decimal('15.00'),
                'price_change_percentage_24h': Decimal('0.78'),
                'api_source': 'metals.live'
            },
            {
                'name': 'Silver (XAG)',
                'asset_type': 'silver',
                'symbol': 'XAG',
                'current_price': Decimal('24.50'),
                'base_currency': 'USD',
                'price_change_24h': Decimal('-0.25'),
                'price_change_percentage_24h': Decimal('-1.01'),
                'api_source': 'metals.live'
            },
            {
                'name': 'Bitcoin (BTC)',
                'asset_type': 'crypto',
                'symbol': 'BTC',
                'current_price': Decimal('45000.00'),
                'base_currency': 'USD',
                'price_change_24h': Decimal('1500.00'),
                'price_change_percentage_24h': Decimal('3.45'),
                'api_source': 'coingecko'
            },
            {
                'name': 'Ethereum (ETH)',
                'asset_type': 'crypto',
                'symbol': 'ETH',
                'current_price': Decimal('2800.00'),
                'base_currency': 'USD',
                'price_change_24h': Decimal('80.00'),
                'price_change_percentage_24h': Decimal('2.94'),
                'api_source': 'coingecko'
            },
            {
                'name': 'Platinum (XPT)',
                'asset_type': 'platinum',
                'symbol': 'XPT',
                'current_price': Decimal('950.00'),
                'base_currency': 'USD',
                'price_change_24h': Decimal('20.00'),
                'price_change_percentage_24h': Decimal('2.15'),
                'api_source': 'metals.live'
            }
        ]
        
        feeds = []
        for feed_data in feeds_data:
            feed, created = RealTimePriceFeed.objects.get_or_create(
                name=feed_data['name'],
                defaults=feed_data
            )
            feeds.append(feed)
        
        return feeds
    
    def create_currency_conversions(self):
        """Create currency conversion rates"""
        conversions_data = [
            {'from_currency': 'USD', 'to_currency': 'EUR', 'exchange_rate': Decimal('0.85')},
            {'from_currency': 'USD', 'to_currency': 'GBP', 'exchange_rate': Decimal('0.73')},
            {'from_currency': 'USD', 'to_currency': 'NGN', 'exchange_rate': Decimal('750.00')},
            {'from_currency': 'USD', 'to_currency': 'BTC', 'exchange_rate': Decimal('0.000022')},
            {'from_currency': 'USD', 'to_currency': 'ETH', 'exchange_rate': Decimal('0.00036')},
        ]
        
        conversions = []
        for conv_data in conversions_data:
            conversion, created = CurrencyConversion.objects.get_or_create(
                from_currency=conv_data['from_currency'],
                to_currency=conv_data['to_currency'],
                defaults={'exchange_rate': conv_data['exchange_rate']}
            )
            conversions.append(conversion)
        
        return conversions
