#!/usr/bin/env python3
"""
Script to create investment categories and items for manual admin addition
Run this script to populate the database with categories and items
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentCategory, InvestmentItem


def create_categories():
    """Create investment categories"""
    print("Creating investment categories...")
    
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
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created category: {category.name}")
        else:
            print(f"ℹ️  Category already exists: {category.name}")
        created_categories.append(category)
    
    return created_categories


def create_investment_items(categories):
    """Create investment items"""
    print("\nCreating investment items...")
    
    # Create a mapping of category names to category objects
    category_map = {cat.name: cat for cat in categories}
    
    items_data = [
        # Precious Metals
        {
            'name': 'Gold Bullion (1 oz)',
            'category': 'Precious Metals',
            'description': 'Pure gold bullion bar, 1 troy ounce. 99.99% pure gold certified by LBMA.',
            'short_description': 'Pure gold bullion bar, 1 troy ounce',
            'current_price_usd': 1950.00,
            'minimum_investment': 195.00,
            'investment_type': 'both',
            'weight': '1 oz',
            'purity': '99.99%',
            'is_featured': True
        },
        {
            'name': 'Silver Bullion (1 oz)',
            'category': 'Precious Metals',
            'description': 'Pure silver bullion bar, 1 troy ounce. 99.9% pure silver certified.',
            'short_description': 'Pure silver bullion bar, 1 troy ounce',
            'current_price_usd': 24.50,
            'minimum_investment': 24.50,
            'investment_type': 'both',
            'weight': '1 oz',
            'purity': '99.9%',
            'is_featured': True
        },
        {
            'name': 'Platinum Bullion (1 oz)',
            'category': 'Precious Metals',
            'description': 'Pure platinum bullion bar, 1 troy ounce. 99.95% pure platinum.',
            'short_description': 'Pure platinum bullion bar, 1 troy ounce',
            'current_price_usd': 920.00,
            'minimum_investment': 92.00,
            'investment_type': 'both',
            'weight': '1 oz',
            'purity': '99.95%',
            'is_featured': False
        },
        
        # Cryptocurrencies
        {
            'name': 'Bitcoin (BTC)',
            'category': 'Cryptocurrencies',
            'description': 'Bitcoin cryptocurrency investment. The world\'s first and most popular cryptocurrency.',
            'short_description': 'Bitcoin cryptocurrency investment',
            'current_price_usd': 45000.00,
            'minimum_investment': 100.00,
            'investment_type': 'both',
            'is_featured': True
        },
        {
            'name': 'Ethereum (ETH)',
            'category': 'Cryptocurrencies',
            'description': 'Ethereum cryptocurrency investment. Smart contract platform and digital currency.',
            'short_description': 'Ethereum cryptocurrency investment',
            'current_price_usd': 2800.00,
            'minimum_investment': 100.00,
            'investment_type': 'both',
            'is_featured': True
        },
        {
            'name': 'Cardano (ADA)',
            'category': 'Cryptocurrencies',
            'description': 'Cardano cryptocurrency investment. Third-generation blockchain platform.',
            'short_description': 'Cardano cryptocurrency investment',
            'current_price_usd': 0.45,
            'minimum_investment': 50.00,
            'investment_type': 'both',
            'is_featured': False
        },
        
        # Real Estate
        {
            'name': 'Luxury Apartment - Lagos',
            'category': 'Real Estate',
            'description': 'Luxury apartment investment in Victoria Island, Lagos. Prime location with high rental yield.',
            'short_description': 'Luxury apartment in Victoria Island, Lagos',
            'current_price_usd': 250000.00,
            'minimum_investment': 5000.00,
            'investment_type': 'investment_only',
            'is_featured': True
        },
        {
            'name': 'Commercial Property - Abuja',
            'category': 'Real Estate',
            'description': 'Commercial property investment in Abuja Central Business District.',
            'short_description': 'Commercial property in Abuja CBD',
            'current_price_usd': 500000.00,
            'minimum_investment': 10000.00,
            'investment_type': 'investment_only',
            'is_featured': False
        },
        
        # Diamonds & Gems
        {
            'name': 'Investment Diamond (1 carat)',
            'category': 'Diamonds & Gems',
            'description': 'High-quality investment diamond, 1 carat, VS1 clarity, D color.',
            'short_description': 'High-quality investment diamond, 1 carat',
            'current_price_usd': 8000.00,
            'minimum_investment': 800.00,
            'investment_type': 'both',
            'is_featured': True
        },
        {
            'name': 'Sapphire (2 carat)',
            'category': 'Diamonds & Gems',
            'description': 'Natural blue sapphire, 2 carat, excellent cut and clarity.',
            'short_description': 'Natural blue sapphire, 2 carat',
            'current_price_usd': 3000.00,
            'minimum_investment': 300.00,
            'investment_type': 'both',
            'is_featured': False
        },
        {
            'name': 'Ruby (1.5 carat)',
            'category': 'Diamonds & Gems',
            'description': 'Natural ruby, 1.5 carat, pigeon blood red color.',
            'short_description': 'Natural ruby, 1.5 carat',
            'current_price_usd': 4500.00,
            'minimum_investment': 450.00,
            'investment_type': 'both',
            'is_featured': False
        },
        
        # Art & Collectibles
        {
            'name': 'Contemporary Art Piece',
            'category': 'Art & Collectibles',
            'description': 'Original contemporary art piece by renowned Nigerian artist.',
            'short_description': 'Original contemporary art piece',
            'current_price_usd': 15000.00,
            'minimum_investment': 1500.00,
            'investment_type': 'investment_only',
            'is_featured': True
        },
        {
            'name': 'Vintage Watch Collection',
            'category': 'Art & Collectibles',
            'description': 'Collection of vintage luxury watches from premium brands.',
            'short_description': 'Collection of vintage luxury watches',
            'current_price_usd': 25000.00,
            'minimum_investment': 2500.00,
            'investment_type': 'both',
            'is_featured': False
        },
        
        # Commodities
        {
            'name': 'Crude Oil Futures',
            'category': 'Commodities',
            'description': 'Crude oil futures contract investment opportunity.',
            'short_description': 'Crude oil futures contract',
            'current_price_usd': 75.00,
            'minimum_investment': 100.00,
            'investment_type': 'investment_only',
            'is_featured': False
        },
        {
            'name': 'Agricultural Commodities',
            'category': 'Commodities',
            'description': 'Diversified agricultural commodities investment portfolio.',
            'short_description': 'Agricultural commodities portfolio',
            'current_price_usd': 5000.00,
            'minimum_investment': 500.00,
            'investment_type': 'investment_only',
            'is_featured': False
        },
        
        # Technology
        {
            'name': 'Tech Startup Fund',
            'category': 'Technology',
            'description': 'Investment fund focused on promising technology startups.',
            'short_description': 'Tech startup investment fund',
            'current_price_usd': 10000.00,
            'minimum_investment': 1000.00,
            'investment_type': 'investment_only',
            'is_featured': True
        },
        {
            'name': 'AI & Machine Learning ETF',
            'category': 'Technology',
            'description': 'Exchange-traded fund focused on artificial intelligence and machine learning companies.',
            'short_description': 'AI & ML focused ETF',
            'current_price_usd': 150.00,
            'minimum_investment': 150.00,
            'investment_type': 'investment_only',
            'is_featured': False
        },
        
        # Healthcare
        {
            'name': 'Healthcare Innovation Fund',
            'category': 'Healthcare',
            'description': 'Investment fund focused on healthcare innovation and biotechnology.',
            'short_description': 'Healthcare innovation fund',
            'current_price_usd': 7500.00,
            'minimum_investment': 750.00,
            'investment_type': 'investment_only',
            'is_featured': False
        }
    ]
    
    created_items = []
    for item_data in items_data:
        category = category_map.get(item_data['category'])
        if not category:
            print(f"❌ Category not found: {item_data['category']}")
            continue
            
        item, created = InvestmentItem.objects.get_or_create(
            name=item_data['name'],
            defaults={
                'category': category,
                'description': item_data['description'],
                'short_description': item_data['short_description'],
                'current_price_usd': item_data['current_price_usd'],
                'minimum_investment': item_data['minimum_investment'],
                'investment_type': item_data['investment_type'],
                'is_active': True,
                'is_featured': item_data.get('is_featured', False)
            }
        )
        
        # Add additional fields if they exist
        if 'weight' in item_data:
            # Convert weight to decimal if it's a string like "1 oz"
            weight_value = item_data['weight']
            if isinstance(weight_value, str) and 'oz' in weight_value:
                # Extract the numeric part
                weight_num = weight_value.replace(' oz', '').strip()
                try:
                    item.weight = Decimal(weight_num)
                except:
                    item.weight = Decimal('1.0')  # Default to 1 oz
            else:
                item.weight = weight_value
        if 'purity' in item_data:
            item.purity = item_data['purity']
        item.save()
        
        if created:
            print(f"✅ Created item: {item.name} - ${item.current_price_usd}")
        else:
            print(f"ℹ️  Item already exists: {item.name}")
        created_items.append(item)
    
    return created_items


def main():
    """Main function"""
    print("🚀 CREATING INVESTMENT CATEGORIES AND ITEMS")
    print("=" * 60)
    
    try:
        # Create categories
        categories = create_categories()
        
        # Create investment items
        items = create_investment_items(categories)
        
        print("\n" + "=" * 60)
        print("🎉 CATEGORIES AND ITEMS CREATION COMPLETED!")
        print(f"\n📊 SUMMARY:")
        print(f"   - Categories created: {len(categories)}")
        print(f"   - Investment items created: {len(items)}")
        
        print(f"\n📋 CATEGORIES:")
        for category in categories:
            print(f"   - {category.name}")
        
        print(f"\n💎 FEATURED ITEMS:")
        featured_items = [item for item in items if item.is_featured]
        for item in featured_items:
            print(f"   - {item.name} (${item.current_price_usd})")
        
        print(f"\n🌐 NEXT STEPS:")
        print("   1. Check Django admin to see all categories and items")
        print("   2. Test the category dropdown in the marketplace")
        print("   3. Browse investment items by category")
        print("   4. Create user investments through admin or frontend")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
