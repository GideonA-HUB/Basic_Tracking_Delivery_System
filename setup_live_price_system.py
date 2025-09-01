#!/usr/bin/env python
"""
Setup script for live price system
This script sets up the real-time price feeds and starts the update process
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import RealTimePriceFeed, InvestmentItem
from investments.price_services import price_service
from investments.tasks import update_real_time_prices, update_investment_item_prices
import logging

logger = logging.getLogger(__name__)

def setup_price_feeds():
    """Set up initial price feeds"""
    print("Setting up price feeds...")
    
    # Define price feeds to create
    price_feeds = [
        {
            'name': 'Bitcoin',
            'asset_type': 'crypto',
            'symbol': 'BTC',
            'current_price': 45000.00,
            'api_source': 'CoinGecko',
            'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        },
        {
            'name': 'Ethereum',
            'asset_type': 'crypto',
            'symbol': 'ETH',
            'current_price': 3000.00,
            'api_source': 'CoinGecko',
            'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
        },
        {
            'name': 'Cardano',
            'asset_type': 'crypto',
            'symbol': 'ADA',
            'current_price': 0.50,
            'api_source': 'CoinGecko',
            'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=cardano&vs_currencies=usd'
        },
        {
            'name': 'Gold (1 oz)',
            'asset_type': 'gold',
            'symbol': 'XAU',
            'current_price': 2000.00,
            'api_source': 'Metals API',
            'api_url': 'https://api.metals.live/v1/spot'
        },
        {
            'name': 'Silver (1 oz)',
            'asset_type': 'silver',
            'symbol': 'XAG',
            'current_price': 25.00,
            'api_source': 'Metals API',
            'api_url': 'https://api.metals.live/v1/spot'
        },
        {
            'name': 'Platinum (1 oz)',
            'asset_type': 'platinum',
            'symbol': 'XPT',
            'current_price': 1000.00,
            'api_source': 'Metals API',
            'api_url': 'https://api.metals.live/v1/spot'
        },
        {
            'name': 'Real Estate Index',
            'asset_type': 'real_estate',
            'symbol': 'REIT_INDEX',
            'current_price': 1500.00,
            'api_source': 'Simulated',
            'api_url': ''
        },
        {
            'name': 'Property Fund',
            'asset_type': 'real_estate',
            'symbol': 'PROPERTY_FUND',
            'current_price': 2500.00,
            'api_source': 'Simulated',
            'api_url': ''
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for feed_data in price_feeds:
        feed, created = RealTimePriceFeed.objects.get_or_create(
            symbol=feed_data['symbol'],
            defaults={
                'name': feed_data['name'],
                'asset_type': feed_data['asset_type'],
                'current_price': feed_data['current_price'],
                'api_source': feed_data['api_source'],
                'api_url': feed_data['api_url'],
                'is_active': True
            }
        )
        
        if created:
            created_count += 1
            print(f'Created price feed: {feed.name} ({feed.symbol})')
        else:
            # Update existing feed
            feed.name = feed_data['name']
            feed.asset_type = feed_data['asset_type']
            feed.api_source = feed_data['api_source']
            feed.api_url = feed_data['api_url']
            feed.is_active = True
            feed.save()
            updated_count += 1
            print(f'Updated price feed: {feed.name} ({feed.symbol})')
    
    print(f'Successfully set up {created_count} new price feeds and updated {updated_count} existing feeds.')
    return created_count + updated_count

def update_prices_with_real_data():
    """Update prices with real data from APIs"""
    print("Updating prices with real data...")
    
    try:
        # Update all prices
        updated_count = price_service.update_all_prices()
        print(f"Updated {updated_count} prices with real data.")
        
        # Update investment item prices
        updated_items = update_investment_item_prices()
        print(f"Updated {updated_items} investment items with new prices.")
        
        return updated_count
        
    except Exception as e:
        print(f"Error updating prices: {e}")
        return 0

def create_sample_investment_items():
    """Create sample investment items if they don't exist"""
    print("Creating sample investment items...")
    
    from investments.models import InvestmentCategory
    
    # Create categories if they don't exist
    categories = {
        'Cryptocurrency': {
            'description': 'Digital currencies and tokens',
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
            print(f"Created category: {cat_name}")
    
    # Create investment items
    items = [
        {
            'name': 'Bitcoin (BTC)',
            'category': 'Cryptocurrency',
            'description': 'The world\'s first and most popular cryptocurrency. Bitcoin is a decentralized digital currency that enables peer-to-peer transactions without intermediaries.',
            'current_price_usd': 45000.00,
            'minimum_investment': 100.00,
            'investment_type': 'both',
            'is_featured': True
        },
        {
            'name': 'Ethereum (ETH)',
            'category': 'Cryptocurrency',
            'description': 'A decentralized platform that enables the creation of smart contracts and decentralized applications (dApps).',
            'current_price_usd': 3000.00,
            'minimum_investment': 100.00,
            'investment_type': 'both',
            'is_featured': True
        },
        {
            'name': 'Cardano (ADA)',
            'category': 'Cryptocurrency',
            'description': 'A blockchain platform for smart contracts, designed to be more secure and scalable than previous generations.',
            'current_price_usd': 0.50,
            'minimum_investment': 50.00,
            'investment_type': 'both',
            'is_featured': False
        },
        {
            'name': 'Gold Bullion (1 oz)',
            'category': 'Precious Metals',
            'description': 'Physical gold bullion, one of the most trusted stores of value throughout history.',
            'current_price_usd': 2000.00,
            'minimum_investment': 100.00,
            'weight': 1.000,
            'purity': '99.99%',
            'investment_type': 'both',
            'is_featured': True
        },
        {
            'name': 'Silver Bullion (1 oz)',
            'category': 'Precious Metals',
            'description': 'Physical silver bullion, an affordable precious metal investment option.',
            'current_price_usd': 25.00,
            'minimum_investment': 50.00,
            'weight': 1.000,
            'purity': '99.9%',
            'investment_type': 'both',
            'is_featured': False
        },
        {
            'name': 'Platinum Bullion (1 oz)',
            'category': 'Precious Metals',
            'description': 'Physical platinum bullion, a rare and valuable precious metal.',
            'current_price_usd': 1000.00,
            'minimum_investment': 500.00,
            'weight': 1.000,
            'purity': '99.95%',
            'investment_type': 'both',
            'is_featured': False
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
                'short_description': item_data['description'][:300],
                'current_price_usd': item_data['current_price_usd'],
                'minimum_investment': item_data['minimum_investment'],
                'investment_type': item_data['investment_type'],
                'is_featured': item_data['is_featured'],
                'is_active': True
            }
        )
        
        if created:
            created_items += 1
            print(f"Created investment item: {item.name}")
        else:
            # Update existing item
            item.current_price_usd = item_data['current_price_usd']
            item.is_featured = item_data['is_featured']
            item.save()
            print(f"Updated investment item: {item.name}")
    
    print(f"Successfully created/updated {created_items} investment items.")
    return created_items

def start_price_updates():
    """Start the price update process"""
    print("Starting price update process...")
    
    try:
        # Run initial price update
        result = update_real_time_prices.delay()
        print(f"Price update task started with ID: {result.id}")
        
        # Schedule regular updates (every 5 minutes)
        from celery import current_app
        current_app.conf.beat_schedule = {
            'update-prices-every-5-minutes': {
                'task': 'investments.tasks.update_real_time_prices',
                'schedule': 300.0,  # 5 minutes
            },
            'update-investment-items-every-10-minutes': {
                'task': 'investments.tasks.update_investment_item_prices',
                'schedule': 600.0,  # 10 minutes
            },
            'cleanup-price-history-daily': {
                'task': 'investments.tasks.cleanup_old_price_history',
                'schedule': 86400.0,  # 24 hours
            },
            'health-check-price-feeds-hourly': {
                'task': 'investments.tasks.health_check_price_feeds',
                'schedule': 3600.0,  # 1 hour
            },
        }
        
        print("Price update schedule configured successfully.")
        return True
        
    except Exception as e:
        print(f"Error starting price updates: {e}")
        return False

def main():
    """Main setup function"""
    print("=== Live Price System Setup ===")
    print()
    
    # Step 1: Set up price feeds
    print("Step 1: Setting up price feeds...")
    setup_price_feeds()
    print()
    
    # Step 2: Create sample investment items
    print("Step 2: Creating sample investment items...")
    create_sample_investment_items()
    print()
    
    # Step 3: Update prices with real data
    print("Step 3: Updating prices with real data...")
    update_prices_with_real_data()
    print()
    
    # Step 4: Start price update process
    print("Step 4: Starting price update process...")
    if start_price_updates():
        print("✅ Live price system setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Start the Django development server: python manage.py runserver")
        print("2. Start Celery worker: celery -A delivery_tracker worker --loglevel=info")
        print("3. Start Celery beat: celery -A delivery_tracker beat --loglevel=info")
        print("4. Visit the investment marketplace to see live price updates")
    else:
        print("❌ Error setting up live price system")
        print("Please check the logs and try again.")

if __name__ == '__main__':
    main()
