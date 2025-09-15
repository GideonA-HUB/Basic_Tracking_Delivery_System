#!/usr/bin/env python
"""
Test script for Boost button functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from investments.services import nowpayments_service
from investments.models import PaymentTransaction
from django.contrib.auth.models import User

def test_boost_functionality():
    """Test the boost payment functionality"""
    print("🚀 TESTING BOOST FUNCTIONALITY")
    print("=" * 50)
    
    try:
        # Test 1: Check NOWPayments service configuration
        print("1. Testing NOWPayments service configuration...")
        print(f"   API Key: {'✅ Configured' if nowpayments_service.api_key else '❌ Missing'}")
        print(f"   IPN Secret: {'✅ Configured' if nowpayments_service.ipn_secret else '❌ Missing'}")
        print(f"   IPN Callback URL: {'✅ Configured' if nowpayments_service.ipn_callback_url else '❌ Missing'}")
        
        # Test 2: Check if boost payment method exists
        print("\n2. Testing boost payment method...")
        if hasattr(nowpayments_service, 'create_boost_payment'):
            print("   ✅ create_boost_payment method exists")
        else:
            print("   ❌ create_boost_payment method not found")
            return False
        
        # Test 3: Test boost payment creation (without actually calling NOWPayments API)
        print("\n3. Testing boost payment creation...")
        try:
            # Get a test user
            user = User.objects.first()
            if not user:
                print("   ❌ No users found in database")
                return False
            
            print(f"   Using test user: {user.username}")
            
            # Test the boost payment creation
            transaction = nowpayments_service.create_boost_payment(user, 740.00)
            
            if transaction:
                print(f"   ✅ Boost payment created successfully")
                print(f"   Payment ID: {transaction.payment_id}")
                print(f"   Amount: ${transaction.amount_usd}")
                print(f"   Type: {transaction.payment_type}")
                print(f"   Status: {transaction.payment_status}")
                
                # Clean up test transaction
                transaction.delete()
                print("   ✅ Test transaction cleaned up")
            else:
                print("   ❌ Failed to create boost payment")
                return False
                
        except Exception as e:
            print(f"   ❌ Error creating boost payment: {e}")
            return False
        
        # Test 4: Check URL patterns
        print("\n4. Testing URL patterns...")
        from django.urls import reverse
        try:
            boost_url = reverse('investments:create-boost-payment')
            print(f"   ✅ Boost payment URL: {boost_url}")
        except Exception as e:
            print(f"   ❌ Error getting boost payment URL: {e}")
            return False
        
        # Test 5: Check existing boost payments
        print("\n5. Checking existing boost payments...")
        boost_payments = PaymentTransaction.objects.filter(payment_type='boost')
        print(f"   Found {boost_payments.count()} boost payments in database")
        
        if boost_payments.exists():
            for payment in boost_payments[:3]:  # Show first 3
                print(f"   - {payment.payment_id}: ${payment.amount_usd} ({payment.payment_status})")
        
        print("\n✅ ALL BOOST FUNCTIONALITY TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during boost functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_boost_functionality()
    if success:
        print("\n🎉 Boost functionality is ready for deployment!")
    else:
        print("\n💥 Boost functionality has issues that need to be fixed!")
        sys.exit(1)
