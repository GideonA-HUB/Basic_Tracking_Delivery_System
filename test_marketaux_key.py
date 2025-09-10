#!/usr/bin/env python
"""
Test script to verify MarketAux API key loading
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.conf import settings
import requests

def test_marketaux_key():
    """Test MarketAux API key loading and API call"""
    print("🔍 TESTING MARKETAUX API KEY LOADING...")
    print("=" * 50)
    
    # Check settings
    marketaux_key = getattr(settings, 'MARKETAUX_API_KEY', '')
    print(f"Settings MARKETAUX_API_KEY: {'✅ Set' if marketaux_key else '❌ Not Set'}")
    
    if marketaux_key:
        print(f"Key length: {len(marketaux_key)}")
        print(f"Key preview: {marketaux_key[:8]}...")
    else:
        print("Key is empty or not found")
    
    # Check environment variable directly
    env_key = os.environ.get('MARKETAUX_API_KEY')
    print(f"\nEnvironment MARKETAUX_API_KEY: {'✅ Set' if env_key else '❌ Not Set'}")
    
    if env_key:
        print(f"Env key length: {len(env_key)}")
        print(f"Env key preview: {env_key[:8]}...")
    
    # Show all environment variables with 'API' or 'KEY'
    print(f"\n🔍 ALL API/KEY ENVIRONMENT VARIABLES:")
    api_vars = {k: v for k, v in os.environ.items() if 'API' in k.upper() or 'KEY' in k.upper()}
    for key, value in api_vars.items():
        if value:
            print(f"   {key}: ✅ Set (length: {len(value)})")
        else:
            print(f"   {key}: ❌ Empty")
    
    # Test API call if key is available
    if marketaux_key:
        print(f"\n🌐 TESTING MARKETAUX API CALL...")
        try:
            url = "https://api.marketaux.com/v1/news/all"
            params = {
                'api_token': marketaux_key,
                'symbols': 'BTC,ETH',
                'limit': 3,
                'language': 'en'
            }
            
            response = requests.get(url, params=params, timeout=15)
            print(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('data', [])
                print(f"✅ API Success: {len(articles)} articles returned")
                
                if articles:
                    first_article = articles[0]
                    print(f"First article: {first_article.get('title', 'No title')[:50]}...")
                    print(f"Source: {first_article.get('source', 'Unknown')}")
                else:
                    print("No articles in response")
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Error message: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ API Exception: {e}")
    else:
        print("\n⚠️  Cannot test API - no key available")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_marketaux_key()
