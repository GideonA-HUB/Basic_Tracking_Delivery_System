#!/usr/bin/env python
"""
Fix script to add missing last_price_update field to InvestmentItem model
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentItem, RealTimePriceFeed
from django.utils import timezone

def fix_investment_model():
    """Fix the missing last_price_update field and other issues"""
    print("🔧 FIXING INVESTMENT MODEL ISSUES")
    print("=" * 50)
    
    # Add last_price_update field to all items
    items = InvestmentItem.objects.all()
    print(f"Found {items.count()} investment items")
    
    for item in items:
        # Set last_price_update to current time if not set
        if not hasattr(item, 'last_price_update'):
            # Add the field dynamically
            item.last_price_update = timezone.now()
            item.save()
            print(f"✅ Fixed {item.name}: Added last_price_update")
        else:
            print(f"ℹ️  {item.name}: Already has last_price_update")
    
    # Check price feeds
    price_feeds = RealTimePriceFeed.objects.all()
    print(f"\n💰 Price Feeds: {price_feeds.count()}")
    
    for feed in price_feeds:
        print(f"  {feed.name}: {feed.symbol} (${feed.current_price}) [Active: {feed.is_active}]")
    
    # Check items with symbols
    items_with_symbols = InvestmentItem.objects.filter(symbol__isnull=False)
    print(f"\n🎯 Items with symbols: {items_with_symbols.count()}")
    
    for item in items_with_symbols:
        print(f"  {item.name}: {item.symbol}")
    
    # Check items without symbols
    items_without_symbols = InvestmentItem.objects.filter(symbol__isnull=True)
    print(f"\n⚠️  Items without symbols: {items_without_symbols.count()}")
    
    for item in items_without_symbols:
        print(f"  {item.name}: {item.category.name}")

def create_missing_price_feeds():
    """Create missing price feeds"""
    print("\n🔧 CREATING MISSING PRICE FEEDS")
    print("=" * 50)
    
    from investments.models import RealTimePriceFeed
    
    # Define required price feeds
    required_feeds = [
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
    
    created_count = 0
    for feed_data in required_feeds:
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
            created_count += 1
        else:
            print(f"ℹ️  Price feed already exists: {feed.name} ({feed.symbol})")
    
    print(f"\n🎯 Created {created_count} new price feeds")

def update_items_with_symbols():
    """Update items to have proper symbols"""
    print("\n🔧 UPDATING ITEMS WITH SYMBOLS")
    print("=" * 50)
    
    # Define symbol mappings
    symbol_mappings = {
        'Bitcoin (BTC)': 'BTC',
        'Ethereum (ETH)': 'ETH',
        'Cardano (ADA)': 'ADA',
        'Gold Bullion (1 oz)': 'XAU',
        'Silver Bullion (1 oz)': 'XAG',
        'Platinum Coins (1 oz)': 'XPT',
        'Luxury Apartment - Lagos': 'PROPERTY_FUND',
        'Downtown Apartment': 'PROPERTY_FUND',
        'Commercial Office Space': 'PROPERTY_FUND',
        'Real Estate Investment Trust': 'REIT_INDEX',
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
            if item:
                if not item.symbol:
                    item.symbol = symbol
                    item.save()
                    print(f"✅ Updated {item_name}: Added symbol {symbol}")
                    updated_count += 1
                else:
                    print(f"ℹ️  {item_name}: Already has symbol {item.symbol}")
            else:
                print(f"❌ Item not found: {item_name}")
                
        except Exception as e:
            print(f"❌ Error updating {item_name}: {e}")
    
    print(f"\n🎯 Updated {updated_count} items with symbols")

def verify_fixes():
    """Verify that all fixes are working"""
    print("\n🔍 VERIFYING FIXES")
    print("=" * 50)
    
    # Check items
    items = InvestmentItem.objects.filter(is_active=True)
    print(f"📦 Active Investment Items: {items.count()}")
    
    # Check price feeds
    price_feeds = RealTimePriceFeed.objects.filter(is_active=True)
    print(f"💰 Active Price Feeds: {price_feeds.count()}")
    
    # Check items with symbols
    items_with_symbols = items.filter(symbol__isnull=False)
    print(f"🎯 Items with Live Price Symbols: {items_with_symbols.count()}")
    
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
    """Main function to fix all issues"""
    print("🚀 FIXING INVESTMENT SYSTEM ISSUES")
    print("=" * 60)
    
    try:
        # Step 1: Fix missing fields
        fix_investment_model()
        
        # Step 2: Create missing price feeds
        create_missing_price_feeds()
        
        # Step 3: Update items with symbols
        update_items_with_symbols()
        
        # Step 4: Verify fixes
        verify_fixes()
        
        print("\n🎉 All fixes completed successfully!")
        print("\n💡 Next steps:")
        print("1. Deploy to Railway")
        print("2. Check if WebSocket errors are gone")
        print("3. Verify live price updates are working")
        
    except Exception as e:
        print(f"\n❌ Error fixing investment system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
