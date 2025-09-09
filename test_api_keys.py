#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.conf import settings

def test_api_keys():
    print("🔑 Testing API Key Configuration...")
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    env_vars = ['NEWSAPI_KEY', 'FINNHUB_API_KEY', 'CRYPTOPANIC_API_KEY', 'COINDESK_API_KEY']
    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        if value != 'NOT SET':
            # Show first 8 characters for security
            masked = value[:8] + '...' if len(value) > 8 else value
            print(f"   {var}: {masked}")
        else:
            print(f"   {var}: NOT SET")
    
    # Check Django settings
    print("\n⚙️ Django Settings:")
    settings_vars = [
        'NEWSAPI_KEY', 'FINNHUB_API_KEY', 'CRYPTOPANIC_API_KEY', 'COINDESK_API_KEY'
    ]
    for var in settings_vars:
        value = getattr(settings, var, 'NOT SET')
        if value != 'NOT SET' and value != '':
            masked = value[:8] + '...' if len(value) > 8 else value
            print(f"   {var}: {masked}")
        else:
            print(f"   {var}: NOT SET")
    
    # Test API key loading
    print("\n🧪 API Key Loading Test:")
    from investments.news_services import NewsAPIService, FinnhubService, CryptoPanicService, CoinDeskService
    
    services = [
        ('NewsAPI', NewsAPIService()),
        ('Finnhub', FinnhubService()),
        ('CryptoPanic', CryptoPanicService()),
        ('CoinDesk', CoinDeskService())
    ]
    
    for name, service in services:
        api_key = getattr(service, 'api_key', '')
        if api_key:
            masked = api_key[:8] + '...' if len(api_key) > 8 else api_key
            print(f"   {name}: {masked}")
        else:
            print(f"   {name}: NO KEY")
    
    print("\n💡 Recommendations:")
    print("1. Set API keys in your local .env file")
    print("2. Or set them as environment variables")
    print("3. On Railway, they should be set in the environment variables section")
    print("4. The news system will work with sample data if no API keys are available")

if __name__ == '__main__':
    test_api_keys()
