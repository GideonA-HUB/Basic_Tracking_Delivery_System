#!/usr/bin/env python
"""
Debug environment variables on Railway
"""
import os
import sys

def debug_environment():
    """Debug all environment variables"""
    print("🔍 ENVIRONMENT VARIABLE DEBUG")
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
    
    # Test Django settings loading
    print(f"\n🔍 DJANGO SETTINGS TEST:")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
        import django
        django.setup()
        
        from django.conf import settings
        settings_key = getattr(settings, 'MARKETAUX_API_KEY', '')
        print(f"   Django settings MARKETAUX_API_KEY: {'✅ Set' if settings_key else '❌ Not Set'}")
        if settings_key:
            print(f"   Settings key length: {len(settings_key)}")
            print(f"   Settings key preview: {settings_key[:8]}...")
        
        # Check if they match
        if marketaux_key and settings_key:
            print(f"   Keys match: {'✅ Yes' if marketaux_key == settings_key else '❌ No'}")
        elif not marketaux_key and not settings_key:
            print(f"   Both empty: ✅ Yes")
        else:
            print(f"   Mismatch: ❌ No")
            
    except Exception as e:
        print(f"   Django setup error: {e}")
    
    print("\n" + "=" * 60)
    print("Environment debug completed!")

if __name__ == "__main__":
    debug_environment()
