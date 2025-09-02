#!/usr/bin/env python
"""
Comprehensive script to set up the complete investment system
This will create categories, items, price feeds, and connect them properly
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import (
    InvestmentCategory, InvestmentItem, RealTimePriceFeed, 
    RealTimePriceHistory, PriceHistory
)
from django.utils import timezone

def create_comprehensive_categories():
    """Create comprehensive investment categories"""
    print("Creating comprehensive investment categories...")
    
    categories_data = [
        {
            'name': 'Precious Metals',
            'description': 'Gold, Silver, Platinum, and other precious metals',
            'icon': 'fas fa-coins',
            'color': '#FFD700'
        },
        {
            'name': 'Cryptocurrencies',
            'description': 'Bitcoin, Ethereum, and other digital assets',
            'icon': 'fab fa-bitcoin',
            'color': '#F7931A'
        },
        {
            'name': 'Real Estate',
            'description': 'Real estate investment opportunities and properties',
            'icon': 'fas fa-building',
            'color': '#4A90E2'
        },
        {
            'name': 'Diamonds & Gems',
            'description': 'Precious stones, diamonds, and jewelry investments',
            'icon': 'fas fa-gem',
            'color': '#E91E63'
        },
        {
            'name': 'Art & Collectibles',
            'description': 'Fine art, collectibles, and luxury items',
            'icon': 'fas fa-palette',
            'color': '#9C27B0'
        },
        {
            'name': 'Commodities',
            'description': 'Oil, gas, agricultural products, and other commodities',
            'icon': 'fas fa-oil-can',
            'color': '#795548'
        },
        {
            'name': 'Technology',
            'description': 'Tech stocks, startups, and technology investments',
            'icon': 'fas fa-microchip',
            'color': '#2196F3'
        },
        {
            'name': 'Healthcare',
            'description': 'Healthcare stocks, pharmaceuticals, and medical investments',
            'icon': 'fas fa-heartbeat',
            'color': '#4CAF50'
        }
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category, created = InvestmentCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'icon': cat_data['icon'],
                'color': cat_data['color'],
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created category: {category.name}")
        else:
            print(f"ℹ️  Category already exists: {category.name}")
        created_categories.append(category)
    
    return created_categories

def create_live_price_feeds():
    """Create live price feeds for real-time updates"""
    print("\nCreating live price feeds...")
    
    price_feeds_data = [
        # Cryptocurrencies
        {
            'name': 'Bitcoin',
            'asset_type': 'crypto',
            'symbol': 'BTC',
            'current_price': Decimal('45000.00'),
            'api_source': 'CoinGecko',
            'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
        },
        {
            'name': 'Ethereum',
            'asset_type': 'crypto',
            'symbol': 'ETH',
            'current_price': Decimal('3000.00'),
            'api_source': 'CoinGecko',
            'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
        },
        {
            'name': 'Cardano',
            'asset_type': 'crypto',
            'symbol': 'ADA',
            'current_price': Decimal('0.50'),
            'api_source': 'CoinGecko',
            'api_url': 'https://api.coingecko.com/api/v3/simple/price?ids=cardano&vs_currencies=usd'
        },
        
        # Precious Metals
        {
            'name': 'Gold (1 oz)',
            'asset_type': 'gold',
            'symbol': 'XAU',
            'current_price': Decimal('2000.00'),
            'api_source': 'Metals API',
            'api_url': 'https://api.metals.live/v1/spot'
        },
        {
            'name': 'Silver (1 oz)',
            'asset_type': 'silver',
            'symbol': 'XAG',
            'current_price': Decimal('25.00'),
            'api_source': 'Metals API',
            'api_url': 'https://api.metals.live/v1/spot'
        },
        {
            'name': 'Platinum (1 oz)',
            'asset_type': 'platinum',
            'symbol': 'XPT',
            'current_price': Decimal('1000.00'),
            'api_source': 'Metals API',
            'api_url': 'https://api.metals.live/v1/spot'
        },
        
        # Real Estate
        {
            'name': 'Real Estate Index',
            'asset_type': 'real_estate',
            'symbol': 'REIT_INDEX',
            'current_price': Decimal('1500.00'),
            'api_source': 'Simulated',
            'api_url': ''
        },
        {
            'name': 'Property Fund',
            'asset_type': 'real_estate',
            'symbol': 'PROPERTY_FUND',
            'current_price': Decimal('2500.00'),
            'api_source': 'Simulated',
            'api_url': ''
        }
    ]
    
    created_feeds = []
    for feed_data in price_feeds_data:
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
            print(f"✅ Created price feed: {feed.name} ({feed.symbol})")
        else:
            print(f"ℹ️  Price feed already exists: {feed.name} ({feed.symbol})")
        created_feeds.append(feed)
    
    return created_feeds

def create_comprehensive_investment_items(categories, price_feeds):
    """Create comprehensive investment items with proper symbol connections"""
    print("\nCreating comprehensive investment items...")
    
    # Create mapping for easy lookup
    category_map = {cat.name: cat for cat in categories}
    feed_map = {feed.symbol: feed for feed in price_feeds}
    
    items_data = [
        # Precious Metals
        {
            'category': category_map['Precious Metals'],
            'name': 'Gold Bullion (1 oz)',
            'description': 'Pure 24K gold bullion coin, perfect for investment and collection.',
            'short_description': '1 oz pure gold bullion coin',
            'current_price_usd': Decimal('1950.00'),
            'symbol': 'XAU',
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
            'category': category_map['Precious Metals'],
            'name': 'Silver Bullion (1 oz)',
            'description': 'Pure 99.9% silver bullion coin, excellent for investment.',
            'short_description': '1 oz pure silver bullion coin',
            'current_price_usd': Decimal('25.00'),
            'symbol': 'XAG',
            'weight': Decimal('1.000'),
            'purity': '99.9%',
            'investment_type': 'both',
            'minimum_investment': Decimal('25.00'),
            'maximum_investment': Decimal('10000.00'),
            'total_available': Decimal('5000.000'),
            'currently_available': Decimal('5000.000'),
            'is_featured': True
        },
        {
            'category': category_map['Precious Metals'],
            'name': 'Platinum Coins (1 oz)',
            'description': 'Pure platinum bullion coins for serious investors.',
            'short_description': '1 oz pure platinum bullion coin',
            'current_price_usd': Decimal('1000.00'),
            'symbol': 'XPT',
            'weight': Decimal('1.000'),
            'purity': '99.95%',
            'investment_type': 'both',
            'minimum_investment': Decimal('100.00'),
            'maximum_investment': Decimal('50000.00'),
            'total_available': Decimal('500.000'),
            'currently_available': Decimal('500.000'),
            'is_featured': False
        },
        
        # Cryptocurrencies
        {
            'category': category_map['Cryptocurrencies'],
            'name': 'Bitcoin (BTC)',
            'description': 'The world\'s first and most popular cryptocurrency.',
            'short_description': 'Digital gold - Bitcoin cryptocurrency',
            'current_price_usd': Decimal('45000.00'),
            'symbol': 'BTC',
            'investment_type': 'investment_only',
            'minimum_investment': Decimal('50.00'),
            'maximum_investment': Decimal('1000000.00'),
            'total_available': Decimal('100.000000'),
            'currently_available': Decimal('100.000000'),
            'is_featured': True
        },
        {
            'category': category_map['Cryptocurrencies'],
            'name': 'Ethereum (ETH)',
            'description': 'The second-largest cryptocurrency by market cap.',
            'short_description': 'Smart contract platform - Ethereum',
            'current_price_usd': Decimal('3000.00'),
            'symbol': 'ETH',
            'investment_type': 'investment_only',
            'minimum_investment': Decimal('50.00'),
            'maximum_investment': Decimal('500000.00'),
            'total_available': Decimal('1000.000000'),
            'currently_available': Decimal('1000.000000'),
            'is_featured': True
        },
        {
            'category': category_map['Cryptocurrencies'],
            'name': 'Cardano (ADA)',
            'description': 'A third-generation blockchain platform.',
            'short_description': 'Proof-of-stake blockchain - Cardano',
            'current_price_usd': Decimal('0.50'),
            'symbol': 'ADA',
            'investment_type': 'investment_only',
            'minimum_investment': Decimal('25.00'),
            'maximum_investment': Decimal('100000.00'),
            'total_available': Decimal('1000000.000000'),
            'currently_available': Decimal('1000000.000000'),
            'is_featured': False
        },
        
        # Real Estate
        {
            'category': category_map['Real Estate'],
            'name': 'Luxury Apartment - Lagos',
            'description': 'Premium apartment in the heart of Lagos, Nigeria.',
            'short_description': 'Luxury apartment in Lagos',
            'current_price_usd': Decimal('250000.00'),
            'symbol': 'PROPERTY_FUND',
            'investment_type': 'both',
            'minimum_investment': Decimal('1000.00'),
            'maximum_investment': Decimal('100000.00'),
            'total_available': Decimal('100.000'),
            'currently_available': Decimal('100.000'),
            'is_featured': True
        },
        {
            'category': category_map['Real Estate'],
            'name': 'Commercial Office Space',
            'description': 'Prime commercial office space in business district.',
            'short_description': 'Commercial office space',
            'current_price_usd': Decimal('500000.00'),
            'symbol': 'PROPERTY_FUND',
            'investment_type': 'investment_only',
            'minimum_investment': Decimal('5000.00'),
            'maximum_investment': Decimal('200000.00'),
            'total_available': Decimal('50.000'),
            'currently_available': Decimal('50.000'),
            'is_featured': False
        },
        {
            'category': category_map['Real Estate'],
            'name': 'Real Estate Investment Trust',
            'description': 'Diversified real estate portfolio investment.',
            'short_description': 'REIT investment fund',
            'current_price_usd': Decimal('75.00'),
            'symbol': 'REIT_INDEX',
            'investment_type': 'investment_only',
            'minimum_investment': Decimal('50.00'),
            'maximum_investment': Decimal('50000.00'),
            'total_available': Decimal('10000.000'),
            'currently_available': Decimal('10000.000'),
            'is_featured': True
        },
        
        # Diamonds & Gems
        {
            'category': category_map['Diamonds & Gems'],
            'name': 'Investment Diamond (1 carat)',
            'description': 'High-quality investment-grade diamond.',
            'short_description': '1 carat investment diamond',
            'current_price_usd': Decimal('8000.00'),
            'investment_type': 'both',
            'minimum_investment': Decimal('1000.00'),
            'maximum_investment': Decimal('8000.00'),
            'total_available': Decimal('100.000'),
            'currently_available': Decimal('100.000'),
            'is_featured': False
        },
        
        # Art & Collectibles
        {
            'category': category_map['Art & Collectibles'],
            'name': 'Contemporary Art Piece',
            'description': 'Original contemporary artwork by emerging artists.',
            'short_description': 'Contemporary art investment',
            'current_price_usd': Decimal('15000.00'),
            'investment_type': 'investment_only',
            'minimum_investment': Decimal('1000.00'),
            'maximum_investment': Decimal('15000.00'),
            'total_available': Decimal('10.000'),
            'currently_available': Decimal('10.000'),
            'is_featured': False
        },
        
        # Technology
        {
            'category': category_map['Technology'],
            'name': 'Tech Startup Fund',
            'description': 'Investment fund focused on technology startups.',
            'short_description': 'Tech startup investment fund',
            'current_price_usd': Decimal('10000.00'),
            'investment_type': 'investment_only',
            'minimum_investment': Decimal('500.00'),
            'maximum_investment': Decimal('50000.00'),
            'total_available': Decimal('1000.000'),
            'currently_available': Decimal('1000.000'),
            'is_featured': False
        }
    ]
    
    created_items = []
    for item_data in items_data:
        # Check if item already exists
        existing_item = InvestmentItem.objects.filter(name=item_data['name']).first()
        
        if existing_item:
            # Update existing item with symbol if it doesn't have one
            if not existing_item.symbol and item_data.get('symbol'):
                existing_item.symbol = item_data['symbol']
                existing_item.save()
                print(f"🔄 Updated existing item with symbol: {existing_item.name} -> {item_data['symbol']}")
            created_items.append(existing_item)
        else:
            # Create new item
            item = InvestmentItem.objects.create(**item_data)
            print(f"✅ Created item: {item.name} (Symbol: {item.symbol})")
            created_items.append(item)
    
    return created_items

def update_existing_items_with_symbols():
    """Update existing items that should have symbols but don't"""
    print("\nUpdating existing items with symbols...")
    
    # Define symbol mappings for existing items
    symbol_mappings = {
        'Bitcoin Investment Fund': 'BTC',
        'Silver Bars (10 oz)': 'XAG',
        'Platinum Bullion (1 oz)': 'XPT',
        'Commercial Property - Abuja': 'PROPERTY_FUND',
        'Commercial Property Fund': 'PROPERTY_FUND',
    }
    
    updated_count = 0
    for item_name, symbol in symbol_mappings.items():
        try:
            item = InvestmentItem.objects.filter(name=item_name, is_active=True).first()
            if item and not item.symbol:
                item.symbol = symbol
                item.save()
                print(f"✅ Updated {item_name}: Added symbol {symbol}")
                updated_count += 1
            elif item and item.symbol:
                print(f"ℹ️  {item_name}: Already has symbol {item.symbol}")
            else:
                print(f"❌ Item not found: {item_name}")
                
        except Exception as e:
            print(f"❌ Error updating {item_name}: {e}")
    
    print(f"Updated {updated_count} items with symbols")

def create_price_history():
    """Create sample price history for items"""
    print("\nCreating price history...")
    
    items = InvestmentItem.objects.filter(is_active=True)
    
    for item in items:
        # Create some price history entries
        base_price = float(item.current_price_usd)
        
        for i in range(7):  # Last 7 days
            date = timezone.now() - timedelta(days=i)
            # Simulate price variation
            variation = random.uniform(-0.05, 0.05)  # ±5%
            price = Decimal(str(base_price * (1 + variation)))
            
            # Create or update price history
            PriceHistory.objects.get_or_create(
                item=item,
                timestamp=date,
                defaults={
                    'price': price,
                    'change_amount': price - item.current_price_usd,
                    'change_percentage': ((price - item.current_price_usd) / item.current_price_usd * 100) if item.current_price_usd > 0 else 0
                }
            )
    
    print(f"Created price history for {items.count()} items")

def verify_system_setup():
    """Verify that the system is properly set up"""
    print("\n🔍 VERIFYING SYSTEM SETUP")
    print("=" * 50)
    
    # Check categories
    categories = InvestmentCategory.objects.filter(is_active=True)
    print(f"📊 Active Categories: {categories.count()}")
    
    # Check price feeds
    price_feeds = RealTimePriceFeed.objects.filter(is_active=True)
    print(f"💰 Active Price Feeds: {price_feeds.count()}")
    
    # Check investment items
    items = InvestmentItem.objects.filter(is_active=True)
    print(f"📦 Active Investment Items: {items.count()}")
    
    # Check items with symbols
    items_with_symbols = items.filter(symbol__isnull=False)
    print(f"🎯 Items with Live Price Symbols: {items_with_symbols.count()}")
    
    # Check items without symbols
    items_without_symbols = items.filter(symbol__isnull=True)
    print(f"⚠️  Items with Static Prices: {items_without_symbols.count()}")
    
    # Check price feed connections
    connected_items = 0
    for item in items_with_symbols:
        feed = RealTimePriceFeed.objects.filter(symbol=item.symbol, is_active=True).first()
        if feed:
            connected_items += 1
            print(f"  ✅ {item.name} -> {feed.name} (${feed.current_price})")
        else:
            print(f"  ❌ {item.name} -> No active price feed for symbol '{item.symbol}'")
    
    print(f"\n🎯 Total Connected Items: {connected_items}/{items_with_symbols.count()}")
    
    if connected_items == items_with_symbols.count():
        print("🎉 All items with symbols are properly connected to price feeds!")
    else:
        print("⚠️  Some items are not properly connected to price feeds")

def main():
    """Main function to set up the complete investment system"""
    print("🚀 SETTING UP COMPLETE INVESTMENT SYSTEM")
    print("=" * 60)
    
    try:
        # Step 1: Create categories
        categories = create_comprehensive_categories()
        
        # Step 2: Create price feeds
        price_feeds = create_live_price_feeds()
        
        # Step 3: Create investment items
        items = create_comprehensive_investment_items(categories, price_feeds)
        
        # Step 4: Update existing items with symbols
        update_existing_items_with_symbols()
        
        # Step 5: Create price history
        create_price_history()
        
        # Step 6: Verify system setup
        verify_system_setup()
        
        print("\n🎉 Investment system setup completed successfully!")
        print("\n💡 Next steps:")
        print("1. Deploy to Railway with Redis add-on")
        print("2. Start Celery worker: celery -A delivery_tracker worker --loglevel=info")
        print("3. Start Celery beat: celery -A delivery_tracker beat --loglevel=info")
        print("4. Test live updates on the website")
        
    except Exception as e:
        print(f"\n❌ Error setting up investment system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
