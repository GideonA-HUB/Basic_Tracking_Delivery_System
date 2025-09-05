#!/usr/bin/env python
"""
Comprehensive fix for the investment system
- Add missing symbols to investment items
- Create missing price feeds
- Fix featured items display
- Ensure real-time price updates work
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentItem, RealTimePriceFeed, PriceHistory, PriceMovementStats
from investments.price_services import price_service
from django.utils import timezone

def fix_investment_system():
    print("🔧 FIXING INVESTMENT SYSTEM")
    print("=" * 50)
    
    # Step 1: Add missing symbols to investment items
    print("\n1️⃣ Adding missing symbols to investment items...")
    symbol_mapping = {
        'Bitcoin (BTC)': 'BTC',
        'Ethereum (ETH)': 'ETH',
        'Cardano (ADA)': 'ADA',
        'Solana (SOL)': 'SOL',
        'Chainlink (LINK)': 'LINK',
        'Polkadot (DOT)': 'DOT',
        'Avalanche (AVAX)': 'AVAX',
        'Polygon (MATIC)': 'MATIC',
        'Gold (1 oz) (XAU)': 'XAU',
        'Silver (1 oz) (XAG)': 'XAG',
        'Platinum (1 oz) (XPT)': 'XPT',
        'Palladium (1 oz) (XPD)': 'XPD',
        'Real Estate Investment Trust': 'REIT_INDEX',
        'Luxury Property Fund': 'LUXURY_PROPERTY',
        'Commercial Real Estate': 'COMM_REIT',
        'Residential Property Fund': 'RES_REIT',
        'Art Investment Fund': 'ART_FUND',
        'Diamond Investment': 'DIAMOND',
        'Oil Futures': 'OIL_FUTURES',
        'Natural Gas': 'NATURAL_GAS',
        'Copper Futures': 'COPPER',
        'Agricultural Commodities': 'AGRI_COMM',
        'Technology Stocks ETF': 'TECH_ETF',
        'Healthcare Stocks ETF': 'HEALTH_ETF',
        'Energy Stocks ETF': 'ENERGY_ETF',
        'Financial Stocks ETF': 'FINANCIAL_ETF',
        'Consumer Goods ETF': 'CONSUMER_ETF',
        'Industrial Stocks ETF': 'INDUSTRIAL_ETF',
        'Utilities ETF': 'UTILITIES_ETF',
        'Materials ETF': 'MATERIALS_ETF',
        'Communication ETF': 'COMMUNICATION_ETF',
        'Real Estate ETF': 'REAL_ESTATE_ETF',
        'Bond ETF': 'BOND_ETF',
    }
    
    updated_symbols = 0
    for item in InvestmentItem.objects.filter(symbol__isnull=True):
        if item.name in symbol_mapping:
            item.symbol = symbol_mapping[item.name]
            item.save()
            updated_symbols += 1
            print(f"   ✅ Added symbol '{item.symbol}' to '{item.name}'")
    
    print(f"   📊 Updated {updated_symbols} items with symbols")
    
    # Step 2: Create missing price feeds
    print("\n2️⃣ Creating missing price feeds...")
    
    # Get existing price feeds
    existing_feeds = set(RealTimePriceFeed.objects.values_list('symbol', flat=True))
    
    # Create price feeds for items that don't have them
    created_feeds = 0
    for item in InvestmentItem.objects.filter(is_active=True, symbol__isnull=False):
        if item.symbol not in existing_feeds:
            # Determine asset type
            asset_type = 'crypto' if item.symbol in ['BTC', 'ETH', 'ADA', 'SOL', 'LINK', 'DOT', 'AVAX', 'MATIC'] else \
                        'gold' if item.symbol == 'XAU' else \
                        'silver' if item.symbol == 'XAG' else \
                        'platinum' if item.symbol == 'XPT' else \
                        'palladium' if item.symbol == 'XPD' else \
                        'real_estate' if 'REIT' in item.symbol or 'PROPERTY' in item.symbol else \
                        'other'
            
            # Create price feed
            feed = RealTimePriceFeed.objects.create(
                name=item.name,
                asset_type=asset_type,
                symbol=item.symbol,
                current_price=item.current_price_usd,
                base_currency='USD',
                price_change_24h=item.price_change_24h or Decimal('0'),
                price_change_percentage_24h=item.price_change_percentage_24h or Decimal('0'),
                is_active=True
            )
            created_feeds += 1
            print(f"   ✅ Created price feed for '{item.name}' ({item.symbol})")
    
    print(f"   📊 Created {created_feeds} new price feeds")
    
    # Step 3: Update all prices with real-time data
    print("\n3️⃣ Updating prices with real-time data...")
    try:
        updated_count = price_service.update_all_prices()
        print(f"   ✅ Updated {updated_count} prices with real-time data")
    except Exception as e:
        print(f"   ⚠️  Error updating prices: {e}")
    
    # Step 4: Ensure featured items are properly set
    print("\n4️⃣ Checking featured items...")
    featured_items = InvestmentItem.objects.filter(is_featured=True)
    print(f"   📊 Found {featured_items.count()} featured items")
    
    # Display featured items
    for item in featured_items:
        print(f"   ⭐ {item.name} - ${item.current_price_usd} ({item.price_change_percentage_24h:+.2f}%)")
    
    # Step 5: Create price history for items
    print("\n5️⃣ Creating initial price history...")
    history_created = 0
    for item in InvestmentItem.objects.filter(is_active=True):
        # Create initial price history entry
        PriceHistory.objects.get_or_create(
            item=item,
            price=item.current_price_usd,
            change_amount=item.price_change_24h or Decimal('0'),
            change_percentage=item.price_change_percentage_24h or Decimal('0'),
            movement_type='unchanged',
            timestamp=timezone.now()
        )
        history_created += 1
    
    print(f"   📊 Created {history_created} price history entries")
    
    # Step 6: Create movement stats for today
    print("\n6️⃣ Creating movement statistics...")
    stats_created = 0
    for item in InvestmentItem.objects.filter(is_active=True):
        stats, created = PriceMovementStats.objects.get_or_create(
            item=item,
            date=timezone.now().date(),
            defaults={
                'increases_today': 0,
                'decreases_today': 0,
                'unchanged_today': 1,  # Start with 1 for the initial entry
                'highest_price_24h': item.current_price_usd,
                'lowest_price_24h': item.current_price_usd,
                'average_price_24h': item.current_price_usd,
            }
        )
        if created:
            stats_created += 1
    
    print(f"   📊 Created {stats_created} movement statistics entries")
    
    # Step 7: Final verification
    print("\n7️⃣ Final verification...")
    
    # Check symbols
    items_with_symbols = InvestmentItem.objects.exclude(symbol__isnull=True).exclude(symbol='').count()
    print(f"   📊 Items with symbols: {items_with_symbols}")
    
    # Check price feeds
    total_feeds = RealTimePriceFeed.objects.count()
    active_feeds = RealTimePriceFeed.objects.filter(is_active=True).count()
    print(f"   📊 Price feeds: {total_feeds} total, {active_feeds} active")
    
    # Check featured items
    featured_count = InvestmentItem.objects.filter(is_featured=True).count()
    print(f"   📊 Featured items: {featured_count}")
    
    # Check price history
    history_count = PriceHistory.objects.count()
    print(f"   📊 Price history entries: {history_count}")
    
    print("\n✅ INVESTMENT SYSTEM FIX COMPLETED!")
    print("=" * 50)
    print("🎯 Next steps:")
    print("   1. Start the live price update service")
    print("   2. Test the WebSocket connections")
    print("   3. Verify featured items display on website")
    print("   4. Check real-time price updates in dashboard")

if __name__ == "__main__":
    fix_investment_system()
