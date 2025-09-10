#!/usr/bin/env python
"""
Startup script with comprehensive environment variable debugging
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def debug_environment_variables():
    """Debug environment variables before Django setup"""
    print("🔍 ENVIRONMENT VARIABLE DEBUG - BEFORE DJANGO SETUP")
    print("=" * 60)
    
    # Check if we're on Railway
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT')
    print(f"Railway Environment: {railway_env or 'Not detected'}")
    
    # Check all environment variables
    print(f"\n🔍 ALL ENVIRONMENT VARIABLES:")
    all_vars = dict(os.environ)
    for key, value in sorted(all_vars.items()):
        if any(keyword in key.upper() for keyword in ['API', 'KEY', 'MARKET', 'NEWS']):
            if value:
                if 'KEY' in key or 'PASSWORD' in key:
                    print(f"   {key}: ✅ Set (length: {len(value)})")
                else:
                    print(f"   {key}: {value}")
            else:
                print(f"   {key}: ❌ Empty")
    
    # Specific check for MarketAux
    marketaux_key = os.environ.get('MARKETAUX_API_KEY')
    print(f"\n🎯 MARKETAUX SPECIFIC CHECK:")
    print(f"   MARKETAUX_API_KEY: {'✅ Set' if marketaux_key else '❌ Not Set'}")
    if marketaux_key:
        print(f"   Key length: {len(marketaux_key)}")
        print(f"   Key preview: {marketaux_key[:8]}...")
        print(f"   Key ends with: ...{marketaux_key[-4:]}")
        print(f"   Key type: {type(marketaux_key)}")
        print(f"   Key repr: {repr(marketaux_key)}")
    
    print("\n" + "=" * 60)

def test_marketaux_api_directly():
    """Test MarketAux API directly without Django"""
    print("🌐 TESTING MARKETAUX API DIRECTLY")
    print("=" * 60)
    
    marketaux_key = os.environ.get('MARKETAUX_API_KEY')
    if not marketaux_key:
        print("❌ No MarketAux API key found in environment variables")
        return False
    
    print(f"✅ Found API key: {marketaux_key[:8]}...")
    
    try:
        import requests
        
        url = "https://api.marketaux.com/v1/news/all"
        params = {
            'api_token': marketaux_key,
            'symbols': 'BTC,ETH',
            'limit': 3,
            'language': 'en'
        }
        
        print(f"Making API request to: {url}")
        print(f"With params: {params}")
        
        response = requests.get(url, params=params, timeout=15)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('data', [])
            print(f"✅ API Success: {len(articles)} articles returned")
            
            if articles:
                first_article = articles[0]
                print(f"First article: {first_article.get('title', 'No title')[:50]}...")
                print(f"Source: {first_article.get('source', 'Unknown')}")
                return True
            else:
                print("No articles in response")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error message: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ API Exception: {e}")
        return False

def main():
    # Debug environment variables first
    debug_environment_variables()
    
    # Test MarketAux API directly
    api_works = test_marketaux_api_directly()
    
    if api_works:
        print("🎉 MarketAux API is working! The issue is in Django settings loading.")
    else:
        print("❌ MarketAux API is not working. Check your API key.")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    # Initialize Django
    django.setup()
    
    print("\n🔍 DJANGO SETTINGS DEBUG - AFTER DJANGO SETUP")
    print("=" * 60)
    
    from django.conf import settings
    settings_key = getattr(settings, 'MARKETAUX_API_KEY', '')
    print(f"Django settings MARKETAUX_API_KEY: {'✅ Set' if settings_key else '❌ Not Set'}")
    if settings_key:
        print(f"Settings key length: {len(settings_key)}")
        print(f"Settings key preview: {settings_key[:8]}...")
    
    # Check if they match
    env_key = os.environ.get('MARKETAUX_API_KEY')
    if env_key and settings_key:
        print(f"Keys match: {'✅ Yes' if env_key == settings_key else '❌ No'}")
    elif not env_key and not settings_key:
        print(f"Both empty: ✅ Yes")
    else:
        print(f"Mismatch: ❌ No")
    
    print("\n" + "=" * 60)
    print("Environment debug completed!")

if __name__ == '__main__':
    main()
