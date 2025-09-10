#!/usr/bin/env python
"""
Railway Environment Variable Fix
This script ensures environment variables are properly loaded on Railway
"""
import os
import sys

def fix_railway_environment():
    """Fix Railway environment variable loading"""
    print("🔧 RAILWAY ENVIRONMENT VARIABLE FIX")
    print("=" * 50)
    
    # Check if we're on Railway
    railway_env = os.environ.get('RAILWAY_ENVIRONMENT')
    print(f"Railway Environment: {railway_env or 'Not detected'}")
    
    # Check current MarketAux key
    marketaux_key = os.environ.get('MARKETAUX_API_KEY')
    print(f"Current MARKETAUX_API_KEY: {'✅ Set' if marketaux_key else '❌ Not Set'}")
    
    if marketaux_key:
        print(f"Key length: {len(marketaux_key)}")
        print(f"Key preview: {marketaux_key[:8]}...")
    else:
        print("❌ No MarketAux API key found!")
        print("Please check your Railway environment variables:")
        print("1. Go to your Railway project dashboard")
        print("2. Navigate to Variables section")
        print("3. Ensure MARKETAUX_API_KEY is set")
        print("4. Redeploy your application")
    
    # Show all environment variables for debugging
    print(f"\n🔍 ALL ENVIRONMENT VARIABLES:")
    all_vars = dict(os.environ)
    for key, value in sorted(all_vars.items()):
        if any(keyword in key.upper() for keyword in ['API', 'KEY', 'MARKET', 'NEWS', 'RAILWAY']):
            if value:
                if 'KEY' in key or 'PASSWORD' in key:
                    print(f"   {key}: ✅ Set (length: {len(value)})")
                else:
                    print(f"   {key}: {value}")
            else:
                print(f"   {key}: ❌ Empty")
    
    print("\n" + "=" * 50)
    print("Railway environment fix completed!")

if __name__ == "__main__":
    fix_railway_environment()
