#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.models import InvestmentItem, InvestmentCategory
from django.db.models import Q

def test_marketplace_data():
    """Test the marketplace data retrieval"""
    print("Testing marketplace data retrieval...")
    
    try:
        # Get categories
        categories = InvestmentCategory.objects.filter(is_active=True)
        print(f"Categories found: {categories.count()}")
        
        # Get all active items
        items = InvestmentItem.objects.filter(is_active=True).select_related('category')
        print(f"Active items found: {items.count()}")
        
        # Get featured items
        featured_items = InvestmentItem.objects.filter(
            is_active=True,
            is_featured=True
        ).select_related('category')[:6]
        print(f"Featured items found: {featured_items.count()}")
        
        # Get trending items
        trending_items = InvestmentItem.objects.filter(
            is_active=True
        ).filter(
            Q(price_change_percentage_24h__gte=5) | 
            Q(price_change_percentage_24h__lte=-5)
        ).select_related('category').order_by('-price_change_percentage_24h')[:6]
        print(f"Trending items found: {trending_items.count()}")
        
        # Print some sample items
        print("\nSample items:")
        for item in items[:5]:
            print(f"- {item.name} (Featured: {item.is_featured}, Category: {item.category.name})")
        
        print("\nMarketplace data retrieval successful!")
        return True
        
    except Exception as e:
        print(f"Error in marketplace data retrieval: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_marketplace_data()
