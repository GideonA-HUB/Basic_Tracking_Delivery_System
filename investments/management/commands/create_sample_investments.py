from django.core.management.base import BaseCommand
from django.utils import timezone
from investments.models import InvestmentCategory, InvestmentItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample investment items for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample investment items...')
        
        # Create categories if they don't exist
        categories = {
            'Cryptocurrency': {
                'description': 'Digital currencies and blockchain assets',
                'icon': 'fas fa-bitcoin',
                'color': '#f7931a'
            },
            'Precious Metals': {
                'description': 'Gold, silver, platinum and other precious metals',
                'icon': 'fas fa-coins',
                'color': '#ffd700'
            },
            'Real Estate': {
                'description': 'Real estate investments and property funds',
                'icon': 'fas fa-building',
                'color': '#4a90e2'
            },
            'Technology': {
                'description': 'Technology stocks and innovation funds',
                'icon': 'fas fa-microchip',
                'color': '#00d4aa'
            }
        }
        
        created_categories = {}
        for cat_name, cat_data in categories.items():
            category, created = InvestmentCategory.objects.get_or_create(
                name=cat_name,
                defaults=cat_data
            )
            created_categories[cat_name] = category
            if created:
                self.stdout.write(f'Created category: {cat_name}')
        
        # Create sample investment items
        items = [
            {
                'name': 'Bitcoin (BTC)',
                'category': 'Cryptocurrency',
                'description': 'The world\'s first and most popular cryptocurrency. Bitcoin is a decentralized digital currency that enables peer-to-peer transactions without intermediaries.',
                'short_description': 'The world\'s first cryptocurrency',
                'current_price_usd': Decimal('45000.00'),
                'price_change_24h': Decimal('1250.00'),
                'price_change_percentage_24h': Decimal('2.85'),
                'minimum_investment': Decimal('100.00'),
                'investment_type': 'both',
                'is_featured': True,
                'is_active': True,
                'main_image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400',
                'additional_image_urls': [
                    'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400',
                    'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400'
                ]
            },
            {
                'name': 'Ethereum (ETH)',
                'category': 'Cryptocurrency',
                'description': 'A decentralized platform that enables the creation of smart contracts and decentralized applications (dApps).',
                'short_description': 'Smart contract platform',
                'current_price_usd': Decimal('3000.00'),
                'price_change_24h': Decimal('-150.00'),
                'price_change_percentage_24h': Decimal('-4.76'),
                'minimum_investment': Decimal('100.00'),
                'investment_type': 'both',
                'is_featured': True,
                'is_active': True,
                'main_image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400',
                'additional_image_urls': [
                    'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400',
                    'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400'
                ]
            },
            {
                'name': 'Gold Bullion (1 oz)',
                'category': 'Precious Metals',
                'description': 'Physical gold bullion, one of the most trusted stores of value throughout history.',
                'short_description': 'Physical gold investment',
                'current_price_usd': Decimal('2000.00'),
                'price_change_24h': Decimal('25.00'),
                'price_change_percentage_24h': Decimal('1.26'),
                'minimum_investment': Decimal('100.00'),
                'weight': Decimal('1.000'),
                'purity': '99.99%',
                'investment_type': 'both',
                'is_featured': True,
                'is_active': True,
                'main_image_url': 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400',
                'additional_image_urls': [
                    'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400',
                    'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400'
                ]
            },
            {
                'name': 'Silver Bullion (1 oz)',
                'category': 'Precious Metals',
                'description': 'Physical silver bullion, an affordable precious metal investment option.',
                'short_description': 'Affordable precious metal',
                'current_price_usd': Decimal('25.00'),
                'price_change_24h': Decimal('-0.50'),
                'price_change_percentage_24h': Decimal('-1.96'),
                'minimum_investment': Decimal('50.00'),
                'weight': Decimal('1.000'),
                'purity': '99.9%',
                'investment_type': 'both',
                'is_featured': False,
                'is_active': True,
                'main_image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400',
                'additional_image_urls': []
            },
            {
                'name': 'Tech Innovation Fund',
                'category': 'Technology',
                'description': 'Diversified portfolio of leading technology companies including AI, cloud computing, and software companies.',
                'short_description': 'Leading tech companies portfolio',
                'current_price_usd': Decimal('150.00'),
                'price_change_24h': Decimal('3.75'),
                'price_change_percentage_24h': Decimal('2.56'),
                'minimum_investment': Decimal('500.00'),
                'investment_type': 'investment_only',
                'is_featured': False,
                'is_active': True,
                'main_image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400',
                'additional_image_urls': []
            },
            {
                'name': 'Real Estate Investment Trust',
                'category': 'Real Estate',
                'description': 'Diversified portfolio of commercial and residential properties across major markets.',
                'short_description': 'Diversified property portfolio',
                'current_price_usd': Decimal('75.00'),
                'price_change_24h': Decimal('1.50'),
                'price_change_percentage_24h': Decimal('2.04'),
                'minimum_investment': Decimal('1000.00'),
                'investment_type': 'investment_only',
                'is_featured': False,
                'is_active': True,
                'main_image_url': 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400',
                'additional_image_urls': []
            },
            {
                'name': 'Cardano (ADA)',
                'category': 'Cryptocurrency',
                'description': 'A blockchain platform for smart contracts, designed to be more secure and scalable than previous generations.',
                'short_description': 'Scalable blockchain platform',
                'current_price_usd': Decimal('0.50'),
                'price_change_24h': Decimal('0.02'),
                'price_change_percentage_24h': Decimal('4.17'),
                'minimum_investment': Decimal('50.00'),
                'investment_type': 'both',
                'is_featured': False,
                'is_active': True,
                'main_image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400',
                'additional_image_urls': []
            },
            {
                'name': 'Platinum Bullion (1 oz)',
                'category': 'Precious Metals',
                'description': 'Physical platinum bullion, a rare and valuable precious metal.',
                'short_description': 'Rare precious metal',
                'current_price_usd': Decimal('1000.00'),
                'price_change_24h': Decimal('-15.00'),
                'price_change_percentage_24h': Decimal('-1.48'),
                'minimum_investment': Decimal('500.00'),
                'weight': Decimal('1.000'),
                'purity': '99.95%',
                'investment_type': 'both',
                'is_featured': False,
                'is_active': True,
                'main_image_url': 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400',
                'additional_image_urls': []
            }
        ]
        
        created_items = 0
        for item_data in items:
            category = created_categories[item_data['category']]
            item, created = InvestmentItem.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    'category': category,
                    'description': item_data['description'],
                    'short_description': item_data['short_description'],
                    'current_price_usd': item_data['current_price_usd'],
                    'price_change_24h': item_data['price_change_24h'],
                    'price_change_percentage_24h': item_data['price_change_percentage_24h'],
                    'minimum_investment': item_data['minimum_investment'],
                    'investment_type': item_data['investment_type'],
                    'is_featured': item_data['is_featured'],
                    'is_active': item_data['is_active'],
                    'main_image_url': item_data['main_image_url'],
                    'additional_image_urls': item_data['additional_image_urls']
                }
            )
            
            # Add weight and purity for precious metals
            if item_data['category'] == 'Precious Metals':
                item.weight = item_data.get('weight')
                item.purity = item_data.get('purity')
                item.save()
            
            if created:
                created_items += 1
                self.stdout.write(f'Created investment item: {item.name}')
            else:
                self.stdout.write(f'Updated investment item: {item.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created/updated {created_items} investment items.'
            )
        )
