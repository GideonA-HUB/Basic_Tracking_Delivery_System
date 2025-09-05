#!/usr/bin/env python
"""
Test script for price updates without Celery dependencies
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.price_services import price_service
from investments.models import InvestmentItem, RealTimePriceFeed
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_price_updates():
    """Test price updates without Celery"""
    try:
        print("🚀 Testing Price Updates")
        print("=" * 50)
        
        # Test crypto prices
        print("📈 Fetching crypto prices...")
        crypto_prices = price_service.fetch_crypto_prices()
        print(f"✅ Fetched {len(crypto_prices)} crypto prices")
        for symbol, data in crypto_prices.items():
            print(f"   {symbol}: ${data['price']} ({data['change_24h']:+.2f})")
        
        # Test metals prices
        print("\n🥇 Fetching metals prices...")
        metals_prices = price_service.fetch_gold_silver_prices()
        print(f"✅ Fetched {len(metals_prices)} metals prices")
        for symbol, data in metals_prices.items():
            print(f"   {symbol}: ${data['price']} ({data['change_24h']:+.2f})")
        
        # Test real estate prices
        print("\n🏠 Fetching real estate prices...")
        re_prices = price_service.fetch_real_estate_indices()
        print(f"✅ Fetched {len(re_prices)} real estate prices")
        for symbol, data in re_prices.items():
            print(f"   {symbol}: ${data['price']} ({data['change_24h']:+.2f})")
        
        # Update all prices
        print("\n🔄 Updating all prices...")
        updated_count = price_service.update_all_prices()
        print(f"✅ Updated {updated_count} price feeds")
        
        # Update investment item prices
        print("\n💼 Updating investment item prices...")
        price_service.update_investment_item_prices()
        
        # Show some updated items
        print("\n📊 Sample Updated Items:")
        items = InvestmentItem.objects.filter(is_active=True)[:5]
        for item in items:
            print(f"   {item.name}: ${item.current_price_usd} ({item.price_change_percentage_24h:+.2f}%)")
        
        print("\n🎉 Price update test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in price update test: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_price_updates()
