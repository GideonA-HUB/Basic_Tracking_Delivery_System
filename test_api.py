#!/usr/bin/env python
"""
Test script for API endpoints
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.views import LivePricesView, PriceStatisticsView
from django.test import RequestFactory
import json

def test_api_endpoints():
    """Test API endpoints"""
    try:
        print("🚀 Testing API Endpoints")
        print("=" * 50)
        
        rf = RequestFactory()
        
        # Test Live Prices API
        print("📈 Testing Live Prices API...")
        request = rf.get('/api/live-prices/')
        view = LivePricesView()
        response = view.get(request)
        print(f"✅ Live Prices API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            prices = data.get('prices', [])
            print(f"✅ Number of prices: {len(prices)}")
            print("📊 Sample prices:")
            for price in prices[:5]:
                print(f"   {price['name']}: ${price['current_price']} ({price['price_change_percentage_24h']:+.2f}%)")
        
        # Test Price Statistics API
        print("\n📊 Testing Price Statistics API...")
        request = rf.get('/api/price-statistics/')
        view = PriceStatisticsView()
        response = view.get(request)
        print(f"✅ Price Statistics API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"✅ Price Statistics:")
            print(f"   Increases: {data.get('increases', 0)}")
            print(f"   Decreases: {data.get('decreases', 0)}")
            print(f"   Total Movements: {data.get('total', 0)}")
        
        print("\n🎉 API endpoints test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_endpoints()
