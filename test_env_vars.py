#!/usr/bin/env python
"""
Simple test script to verify environment variables
"""
import os

def test_environment_variables():
    """Test environment variables"""
    print("🔍 TESTING ENVIRONMENT VARIABLES")
    print("=" * 50)
    
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
    
    print("\n" + "=" * 50)
    print("Environment test completed!")

if __name__ == "__main__":
    test_environment_variables()
