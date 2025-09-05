#!/usr/bin/env python
"""
Fix remaining investment items without symbols
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentItem, RealTimePriceFeed

def fix_remaining_symbols():
    print("🔧 FIXING REMAINING SYMBOLS")
    print("=" * 40)
    
    # Get items without symbols
    items_without_symbols = InvestmentItem.objects.filter(symbol__isnull=True)
    print(f"Found {items_without_symbols.count()} items without symbols")
    
    # Extended symbol mapping
    symbol_mapping = {
        'Tech Startup Fund': 'TECH_FUND',
        'Contemporary Art Piece': 'ART_PIECE',
        'Luxury Apartment - Lagos': 'LUXURY_APT',
        'Investment Diamond (1 carat)': 'DIAMOND_1CT',
        'Oil Futures Contract': 'OIL_FUTURES',
        'Natural Gas Futures': 'NATURAL_GAS',
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
        'Commercial Real Estate': 'COMM_REIT',
        'Residential Property Fund': 'RES_REIT',
        'Art Investment Fund': 'ART_FUND',
        'Diamond Investment': 'DIAMOND_INV',
        'Antique Sculpture': 'ANTIQUE_SCULPTURE',
        'Diamond Ring (2 carat)': 'DIAMOND_2CT',
        'Downtown Apartment': 'DOWNTOWN_APT',
        'Bitcoin Investment Fund': 'BTC_FUND',
        'Ethereum Investment Fund': 'ETH_FUND',
        'Gold Investment Fund': 'GOLD_FUND',
        'Silver Investment Fund': 'SILVER_FUND',
        'Platinum Investment Fund': 'PLATINUM_FUND',
        'Real Estate Investment Fund': 'REIT_FUND',
        'Crypto Portfolio Fund': 'CRYPTO_FUND',
    }
    
    updated_count = 0
    for item in items_without_symbols:
        if item.name in symbol_mapping:
            item.symbol = symbol_mapping[item.name]
            item.save()
            updated_count += 1
            print(f"   ✅ Added symbol '{item.symbol}' to '{item.name}'")
        else:
            # Generate a symbol from the name
            symbol = item.name.upper().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').replace(',', '')[:20]
            item.symbol = symbol
            item.save()
            updated_count += 1
            print(f"   ✅ Generated symbol '{item.symbol}' for '{item.name}'")
    
    print(f"\n📊 Updated {updated_count} items with symbols")
    
    # Create price feeds for new symbols
    print("\n🔄 Creating price feeds for new symbols...")
    existing_feeds = set(RealTimePriceFeed.objects.values_list('symbol', flat=True))
    
    created_feeds = 0
    for item in InvestmentItem.objects.filter(is_active=True, symbol__isnull=False):
        if item.symbol not in existing_feeds:
            # Determine asset type
            asset_type = 'crypto' if any(crypto in item.symbol for crypto in ['BTC', 'ETH', 'CRYPTO']) else \
                        'gold' if 'GOLD' in item.symbol else \
                        'silver' if 'SILVER' in item.symbol else \
                        'platinum' if 'PLATINUM' in item.symbol else \
                        'real_estate' if any(re in item.symbol for re in ['REIT', 'PROPERTY', 'APT', 'REAL_ESTATE']) else \
                        'art' if 'ART' in item.symbol else \
                        'diamond' if 'DIAMOND' in item.symbol else \
                        'other'
            
            # Create price feed
            feed = RealTimePriceFeed.objects.create(
                name=item.name,
                asset_type=asset_type,
                symbol=item.symbol,
                current_price=item.current_price_usd,
                base_currency='USD',
                price_change_24h=item.price_change_24h or 0,
                price_change_percentage_24h=item.price_change_percentage_24h or 0,
                is_active=True
            )
            created_feeds += 1
            print(f"   ✅ Created price feed for '{item.name}' ({item.symbol})")
    
    print(f"\n📊 Created {created_feeds} new price feeds")
    
    # Final verification
    print("\n🔍 Final verification...")
    items_with_symbols = InvestmentItem.objects.exclude(symbol__isnull=True).exclude(symbol='').count()
    total_feeds = RealTimePriceFeed.objects.count()
    
    print(f"   📊 Items with symbols: {items_with_symbols}")
    print(f"   📊 Total price feeds: {total_feeds}")
    
    print("\n✅ SYMBOL FIX COMPLETED!")

if __name__ == "__main__":
    fix_remaining_symbols()
