#!/usr/bin/env python
"""
Production Database Fix Script for Railway
Run this on Railway to fix the missing data and price feeds
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django with production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings_production')
django.setup()

from investments.models import InvestmentItem, RealTimePriceFeed, InvestmentCategory
from django.utils import timezone

def fix_production_database():
    """Fix all production database issues"""
    print("🚀 FIXING PRODUCTION DATABASE ON RAILWAY")
    print("=" * 60)
    
    # Step 1: Fix missing last_price_update fields
    print("\n🔧 STEP 1: Fixing missing last_price_update fields...")
    items = InvestmentItem.objects.all()
    print(f"Found {items.count()} investment items")
    
    fixed_count = 0
    for item in items:
        if not hasattr(item, 'last_price_update') or item.last_price_update is None:
            item.last_price_update = timezone.now()
            item.save()
            print(f"✅ Fixed {item.name}: Added last_price_update")
            fixed_count += 1
        else:
            print(f"ℹ️  {item.name}: Already has last_price_update")
    
    print(f"🎯 Fixed {fixed_count} items with missing last_price_update")
    
    # Step 2: Create missing price feeds
    print("\n🔧 STEP 2: Creating missing price feeds...")
    create_price_feeds()
    
    # Step 3: Update items with symbols
    print("\n🔧 STEP 3: Updating items with symbols...")
    update_items_with_symbols()
    
    # Step 4: Verify fixes
    print("\n🔍 STEP 4: Verifying fixes...")
    verify_fixes()
    
    print("\n🎉 PRODUCTION DATABASE FIX COMPLETED!")
    print("💡 Your live price updates should now work!")

def create_price_feeds():
    """Create all required price feeds"""
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
                'is_active': True,
                'last_updated': timezone.now()
            }
        )
        if created:
            print(f"✅ Created price feed: {feed.name} ({feed.symbol})")
            created_count += 1
        else:
            print(f"ℹ️  Price feed already exists: {feed.name} ({feed.symbol})")
    
    print(f"🎯 Total price feeds: {RealTimePriceFeed.objects.count()}")

def update_items_with_symbols():
    """Update items to have proper symbols"""
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
    
    print(f"🎯 Updated {updated_count} items with symbols")

def verify_fixes():
    """Verify that all fixes are working"""
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

if __name__ == "__main__":
    try:
        fix_production_database()
    except Exception as e:
        print(f"\n❌ Error fixing production database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
