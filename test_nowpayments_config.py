#!/usr/bin/env python
"""
Test script to verify NOWPayments configuration
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings_production')
django.setup()

from investments.services import nowpayments_service

def test_nowpayments_config():
    """Test NOWPayments configuration"""
    print("🔍 Testing NOWPayments Configuration...")
    print("=" * 50)
    
    # Test service initialization
    print(f"API Key: {'✅ Configured' if nowpayments_service.api_key else '❌ Missing'}")
    if nowpayments_service.api_key:
        print(f"API Key Preview: {nowpayments_service.api_key[:10]}...")
        print(f"API Key Length: {len(nowpayments_service.api_key)}")
    
    print(f"IPN Secret: {'✅ Configured' if nowpayments_service.ipn_secret else '❌ Missing'}")
    if nowpayments_service.ipn_secret:
        print(f"IPN Secret Preview: {nowpayments_service.ipn_secret[:10]}...")
    
    print(f"IPN Callback URL: {'✅ Configured' if nowpayments_service.ipn_callback_url else '❌ Missing'}")
    if nowpayments_service.ipn_callback_url:
        print(f"IPN URL: {nowpayments_service.ipn_callback_url}")
    
    print(f"API URL: {nowpayments_service.api_url}")
    
    print("\n🔧 Configuration Validation:")
    print("=" * 30)
    
    # Test configuration validation
    is_valid = nowpayments_service.validate_configuration()
    print(f"Configuration Valid: {'✅ Yes' if is_valid else '❌ No'}")
    
    if not is_valid:
        print("\n❌ Configuration Issues Found:")
        print("Please check the following:")
        print("1. NOWPAYMENTS_API_KEY environment variable")
        print("2. NOWPAYMENTS_IPN_SECRET environment variable") 
        print("3. NOWPAYMENTS_IPN_URL environment variable")
        print("\nRequired values:")
        print("NOWPAYMENTS_IPN_URL=https://meridian-asset-logistics.up.railway.app/investments/api/payments/ipn/")
    else:
        print("\n✅ Configuration looks good!")
        print("You can now test payment creation.")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_nowpayments_config()
