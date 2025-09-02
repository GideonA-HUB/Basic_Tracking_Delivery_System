#!/usr/bin/env python
"""
Script to update existing investment items with symbols for live price updates
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentItem, RealTimePriceFeed

def update_investment_symbols():
    """Update investment items with symbols to enable live price updates"""
    print("🔧 UPDATING INVESTMENT ITEM SYMBOLS")
    print("=" * 50)
    
    # Define symbol mappings for existing items
    symbol_mappings = {
        # Cryptocurrencies
        'Bitcoin (BTC)': 'BTC',
        'Ethereum (ETH)': 'ETH',
        'Cardano (ADA)': 'ADA',
        'Bitcoin Investment Fund': 'BTC',
        
        # Precious Metals
        'Gold Bullion (1 oz)': 'XAU',
        'Silver Bullion (1 oz)': 'XAG',
        'Platinum Coins (1 oz)': 'XPT',
        'Silver Bars (10 oz)': 'XAG',
        
        # Real Estate
        'Luxury Apartment - Lagos': 'PROPERTY_FUND',
        'Downtown Apartment': 'PROPERTY_FUND',
        'Commercial Office Space': 'PROPERTY_FUND',
        'Real Estate Investment Trust': 'REIT_INDEX',
        
        # Other items will keep their current prices (no live updates)
    }
    
    updated_count = 0
    
    for item_name, symbol in symbol_mappings.items():
        try:
            item = InvestmentItem.objects.filter(name=item_name, is_active=True).first()
            if item:
                old_symbol = item.symbol
                item.symbol = symbol
                item.save()
                
                # Check if there's a matching price feed
                price_feed = RealTimePriceFeed.objects.filter(symbol=symbol, is_active=True).first()
                if price_feed:
                    print(f"✅ {item_name}: {old_symbol} → {symbol} (Price Feed: ${price_feed.current_price})")
                    updated_count += 1
                else:
                    print(f"⚠️ {item_name}: {old_symbol} → {symbol} (No price feed found)")
            else:
                print(f"❌ Item not found: {item_name}")
                
        except Exception as e:
            print(f"❌ Error updating {item_name}: {e}")
    
    print(f"\n🎯 Updated {updated_count} investment items with symbols")
    
    # Show items that still need symbols
    print("\n📋 Items without symbols (will use static prices):")
    items_without_symbols = InvestmentItem.objects.filter(is_active=True, symbol__isnull=True)
    for item in items_without_symbols:
        print(f"  - {item.name} (Category: {item.category.name})")
    
    return updated_count

def verify_price_feed_connections():
    """Verify that investment items are properly connected to price feeds"""
    print("\n🔍 VERIFYING PRICE FEED CONNECTIONS")
    print("=" * 50)
    
    items_with_symbols = InvestmentItem.objects.filter(is_active=True, symbol__isnull=False)
    
    for item in items_with_symbols:
        price_feed = RealTimePriceFeed.objects.filter(symbol=item.symbol, is_active=True).first()
        
        if price_feed:
            price_diff = abs(float(item.current_price_usd) - float(price_feed.current_price))
            price_diff_percent = (price_diff / float(item.current_price_usd)) * 100 if float(item.current_price_usd) > 0 else 0
            
            status = "✅" if price_diff_percent < 5 else "⚠️"
            print(f"{status} {item.name}: Item ${item.current_price_usd} vs Feed ${price_feed.current_price} (Diff: ${price_diff:.2f}, {price_diff_percent:.1f}%)")
        else:
            print(f"❌ {item.name}: Symbol '{item.symbol}' has no price feed")

def main():
    """Main function"""
    print("🚀 Investment Symbol Update Script")
    print("=" * 50)
    
    # Update symbols
    updated_count = update_investment_symbols()
    
    # Verify connections
    verify_price_feed_connections()
    
    print(f"\n🎉 Script completed! {updated_count} items updated with symbols.")
    print("\n💡 Next steps:")
    print("1. Deploy to Railway")
    print("2. Test live updates on website")
    print("3. Run price simulation: python simulate_live_updates.py --single")

if __name__ == "__main__":
    main()
