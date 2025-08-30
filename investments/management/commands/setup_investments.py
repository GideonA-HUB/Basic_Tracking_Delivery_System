from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from investments.models import (
    InvestmentCategory, InvestmentItem, PriceHistory
)
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Set up sample investment data for the investment system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up investment system...')
        
        # Create investment categories
        categories = self.create_categories()
        
        # Create investment items
        items = self.create_investment_items(categories)
        
        # Create price history for items
        self.create_price_history(items)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(categories)} categories and {len(items)} investment items'
            )
        )

    def create_categories(self):
        """Create investment categories"""
        categories_data = [
            {
                'name': 'Precious Metals',
                'description': 'Gold, silver, platinum, and other precious metals',
                'icon': 'fas fa-coins',
                'color': '#FFD700'
            },
            {
                'name': 'Real Estate',
                'description': 'Residential and commercial real estate properties',
                'icon': 'fas fa-building',
                'color': '#4A90E2'
            },
            {
                'name': 'Diamonds & Gems',
                'description': 'Precious stones and jewelry',
                'icon': 'fas fa-gem',
                'color': '#E91E63'
            },
            {
                'name': 'Fine Art',
                'description': 'Paintings, sculptures, and collectibles',
                'icon': 'fas fa-palette',
                'color': '#9C27B0'
            },
            {
                'name': 'Cryptocurrency',
                'description': 'Digital assets and blockchain investments',
                'icon': 'fas fa-bitcoin-sign',
                'color': '#FF9800'
            },
            {
                'name': 'Wine & Spirits',
                'description': 'Fine wines and rare spirits',
                'icon': 'fas fa-wine-glass',
                'color': '#8BC34A'
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = InvestmentCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
            categories.append(category)
        
        return categories

    def create_investment_items(self, categories):
        """Create sample investment items"""
        items_data = [
            # Precious Metals
            {
                'category': categories[0],  # Precious Metals
                'name': 'Gold Bullion (1 oz)',
                'description': 'Pure 24K gold bullion coin, perfect for investment and collection.',
                'short_description': '1 oz pure gold bullion coin',
                'current_price_usd': Decimal('1950.00'),
                'weight': Decimal('1.000'),
                'purity': '24K (99.99%)',
                'investment_type': 'both',
                'minimum_investment': Decimal('100.00'),
                'maximum_investment': Decimal('100000.00'),
                'total_available': Decimal('1000.000'),
                'currently_available': Decimal('1000.000'),
                'is_featured': True
            },
            {
                'category': categories[0],
                'name': 'Silver Bars (10 oz)',
                'description': 'High-quality silver bars with 99.9% purity, excellent investment option.',
                'short_description': '10 oz pure silver bars',
                'current_price_usd': Decimal('250.00'),
                'weight': Decimal('10.000'),
                'purity': '99.9%',
                'investment_type': 'both',
                'minimum_investment': Decimal('50.00'),
                'maximum_investment': Decimal('50000.00'),
                'total_available': Decimal('5000.000'),
                'currently_available': Decimal('5000.000'),
                'is_featured': False
            },
            {
                'category': categories[0],
                'name': 'Platinum Coins (1 oz)',
                'description': 'Rare platinum coins with high investment potential.',
                'short_description': '1 oz platinum investment coins',
                'current_price_usd': Decimal('1200.00'),
                'weight': Decimal('1.000'),
                'purity': '99.95%',
                'investment_type': 'investment_only',
                'minimum_investment': Decimal('200.00'),
                'maximum_investment': Decimal('100000.00'),
                'total_available': Decimal('500.000'),
                'currently_available': Decimal('500.000'),
                'is_featured': False
            },
            
            # Real Estate
            {
                'category': categories[1],  # Real Estate
                'name': 'Downtown Apartment',
                'description': 'Modern 2-bedroom apartment in prime downtown location with rental income potential.',
                'short_description': 'Prime downtown apartment investment',
                'current_price_usd': Decimal('450000.00'),
                'investment_type': 'investment_only',
                'minimum_investment': Decimal('5000.00'),
                'maximum_investment': Decimal('450000.00'),
                'total_available': Decimal('1.000'),
                'currently_available': Decimal('1.000'),
                'is_featured': True
            },
            {
                'category': categories[1],
                'name': 'Commercial Office Space',
                'description': 'Premium office space in business district with long-term lease agreements.',
                'short_description': 'Commercial office space investment',
                'current_price_usd': Decimal('1200000.00'),
                'investment_type': 'investment_only',
                'minimum_investment': Decimal('10000.00'),
                'maximum_investment': Decimal('1200000.00'),
                'total_available': Decimal('1.000'),
                'currently_available': Decimal('1.000'),
                'is_featured': False
            },
            
            # Diamonds & Gems
            {
                'category': categories[2],  # Diamonds & Gems
                'name': 'Diamond Ring (2 carat)',
                'description': 'Exquisite diamond ring with VS1 clarity and excellent cut.',
                'short_description': '2 carat diamond ring',
                'current_price_usd': Decimal('25000.00'),
                'weight': Decimal('2.000'),
                'purity': 'VS1, Excellent Cut',
                'investment_type': 'both',
                'minimum_investment': Decimal('1000.00'),
                'maximum_investment': Decimal('25000.00'),
                'total_available': Decimal('10.000'),
                'currently_available': Decimal('10.000'),
                'is_featured': True
            },
            {
                'category': categories[2],
                'name': 'Sapphire Necklace',
                'description': 'Beautiful sapphire necklace with 18K gold setting.',
                'short_description': 'Sapphire and gold necklace',
                'current_price_usd': Decimal('8500.00'),
                'weight': Decimal('15.000'),
                'purity': 'Natural Sapphire, 18K Gold',
                'investment_type': 'delivery_only',
                'minimum_investment': Decimal('8500.00'),
                'maximum_investment': Decimal('8500.00'),
                'total_available': Decimal('5.000'),
                'currently_available': Decimal('5.000'),
                'is_featured': False
            },
            
            # Fine Art
            {
                'category': categories[3],  # Fine Art
                'name': 'Contemporary Painting',
                'description': 'Original contemporary artwork by renowned artist, excellent investment piece.',
                'short_description': 'Contemporary art investment',
                'current_price_usd': Decimal('15000.00'),
                'investment_type': 'investment_only',
                'minimum_investment': Decimal('1000.00'),
                'maximum_investment': Decimal('15000.00'),
                'total_available': Decimal('1.000'),
                'currently_available': Decimal('1.000'),
                'is_featured': False
            },
            {
                'category': categories[3],
                'name': 'Antique Sculpture',
                'description': 'Rare antique sculpture with historical significance.',
                'short_description': 'Antique sculpture investment',
                'current_price_usd': Decimal('75000.00'),
                'investment_type': 'investment_only',
                'minimum_investment': Decimal('5000.00'),
                'maximum_investment': Decimal('75000.00'),
                'total_available': Decimal('1.000'),
                'currently_available': Decimal('1.000'),
                'is_featured': True
            },
            
            # Cryptocurrency
            {
                'category': categories[4],  # Cryptocurrency
                'name': 'Bitcoin Investment Fund',
                'description': 'Managed Bitcoin investment fund with professional trading strategies.',
                'short_description': 'Bitcoin investment fund',
                'current_price_usd': Decimal('45000.00'),
                'investment_type': 'investment_only',
                'minimum_investment': Decimal('100.00'),
                'maximum_investment': Decimal('100000.00'),
                'total_available': Decimal('1000.000'),
                'currently_available': Decimal('1000.000'),
                'is_featured': True
            },
            {
                'category': categories[4],
                'name': 'Ethereum Staking',
                'description': 'Ethereum staking opportunity with competitive returns.',
                'short_description': 'Ethereum staking investment',
                'current_price_usd': Decimal('3200.00'),
                'investment_type': 'investment_only',
                'minimum_investment': Decimal('100.00'),
                'maximum_investment': Decimal('50000.00'),
                'total_available': Decimal('5000.000'),
                'currently_available': Decimal('5000.000'),
                'is_featured': False
            },
            
            # Wine & Spirits
            {
                'category': categories[5],  # Wine & Spirits
                'name': 'Vintage Wine Collection',
                'description': 'Premium vintage wine collection with investment-grade bottles.',
                'short_description': 'Vintage wine investment',
                'current_price_usd': Decimal('12000.00'),
                'investment_type': 'both',
                'minimum_investment': Decimal('500.00'),
                'maximum_investment': Decimal('12000.00'),
                'total_available': Decimal('10.000'),
                'currently_available': Decimal('10.000'),
                'is_featured': False
            },
            {
                'category': categories[5],
                'name': 'Rare Whiskey Collection',
                'description': 'Exclusive collection of rare and aged whiskey bottles.',
                'short_description': 'Rare whiskey investment',
                'current_price_usd': Decimal('8500.00'),
                'investment_type': 'both',
                'minimum_investment': Decimal('500.00'),
                'maximum_investment': Decimal('8500.00'),
                'total_available': Decimal('20.000'),
                'currently_available': Decimal('20.000'),
                'is_featured': False
            }
        ]
        
        items = []
        for item_data in items_data:
            # Add some price variation
            base_price = item_data['current_price_usd']
            price_change = base_price * Decimal(random.uniform(-0.05, 0.08))  # -5% to +8%
            current_price = base_price + price_change
            
            item_data['current_price_usd'] = current_price
            item_data['price_change_24h'] = price_change
            item_data['price_change_percentage_24h'] = (price_change / base_price) * 100
            
            item, created = InvestmentItem.objects.get_or_create(
                name=item_data['name'],
                defaults=item_data
            )
            if created:
                self.stdout.write(f'Created item: {item.name} - ${item.current_price_usd}')
            items.append(item)
        
        return items

    def create_price_history(self, items):
        """Create sample price history for items"""
        from django.utils import timezone
        import random
        
        for item in items:
            # Create 30 days of price history
            base_price = item.current_price_usd
            current_date = timezone.now()
            
            for i in range(30):
                # Generate realistic price movements
                price_change = base_price * Decimal(random.uniform(-0.02, 0.03))  # -2% to +3%
                new_price = base_price + price_change
                change_percentage = (price_change / base_price) * 100
                
                PriceHistory.objects.create(
                    item=item,
                    price=new_price,
                    change_amount=price_change,
                    change_percentage=change_percentage,
                    timestamp=current_date - timezone.timedelta(days=30-i)
                )
                
                base_price = new_price
            
            self.stdout.write(f'Created price history for: {item.name}')
