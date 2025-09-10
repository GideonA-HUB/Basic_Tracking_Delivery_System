#!/usr/bin/env python
"""
Railway Environment Variable Checker
This script helps debug environment variable loading issues on Railway
"""
import os
import sys
from pathlib import Path

def check_railway_environment():
    """Check Railway environment variables"""
    print("🚀 RAILWAY ENVIRONMENT VARIABLE CHECKER")
    print("=" * 60)
    
    # Check if we're running on Railway
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT')
    print(f"Railway Environment: {railway_env or 'Not detected'}")
    
    # Check for Railway-specific variables
    railway_vars = [
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_PROJECT_ID',
        'RAILWAY_SERVICE_ID',
        'RAILWAY_DEPLOYMENT_ID',
        'PORT',
        'DATABASE_URL',
        'REDIS_URL'
    ]
    
    print(f"\n🔍 RAILWAY SYSTEM VARIABLES:")
    for var in railway_vars:
        value = os.environ.get(var)
        if value:
            if 'URL' in var or 'PASSWORD' in var:
                print(f"   {var}: ✅ Set (length: {len(value)})")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   {var}: ❌ Not Set")
    
    # Check for API keys
    print(f"\n🔍 API KEY VARIABLES:")
    api_vars = {k: v for k, v in os.environ.items() if 'API' in k.upper() or 'KEY' in k.upper()}
    for key, value in api_vars.items():
        if value:
            print(f"   {key}: ✅ Set (length: {len(value)})")
        else:
            print(f"   {key}: ❌ Empty")
    
    # Check for news-related variables
    print(f"\n🔍 NEWS-RELATED VARIABLES:")
    news_vars = {k: v for k, v in os.environ.items() if any(keyword in k.upper() for keyword in ['NEWS', 'MARKET', 'FINN', 'CRYPTO', 'COIN'])}
    for key, value in news_vars.items():
        if value:
            print(f"   {key}: ✅ Set (length: {len(value)})")
        else:
            print(f"   {key}: ❌ Empty")
    
    # Show all environment variables (for debugging)
    print(f"\n🔍 ALL ENVIRONMENT VARIABLES:")
    all_vars = dict(os.environ)
    for key, value in sorted(all_vars.items()):
        if any(keyword in key.upper() for keyword in ['NEWS', 'FINN', 'CRYPTO', 'COIN', 'API', 'KEY', 'MARKET', 'RAILWAY']):
            if value:
                if 'URL' in key or 'PASSWORD' in key or 'KEY' in key:
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
    
    print("\n" + "=" * 60)
    print("Environment check completed!")

if __name__ == "__main__":
    check_railway_environment()
