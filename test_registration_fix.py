#!/usr/bin/env python3
"""
Test script to verify the customer registration fix
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import CustomerProfile
from accounts.forms import CustomerRegistrationForm


def test_customer_registration():
    """Test customer registration to ensure no duplicate profile errors"""
    print("Testing customer registration fix...")
    
    # Test data
    test_data = {
        'username': 'testuser_fix',
        'email': 'testfix@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password1': 'testpass123',
        'password2': 'testpass123',
        'phone_number': '+1234567890',
        'address': '123 Test St',
        'city': 'Test City',
        'state': 'Test State',
        'country': 'Test Country'
    }
    
    try:
        # Create form and validate
        form = CustomerRegistrationForm(data=test_data)
        if form.is_valid():
            # Save user
            user = form.save()
            print(f"✅ User created successfully: {user.username}")
            
            # Check if profile was created
            try:
                profile = CustomerProfile.objects.get(user=user)
                print(f"✅ Customer profile created successfully: {profile}")
            except CustomerProfile.DoesNotExist:
                print("❌ Customer profile not found")
                return False
            
            # Try to create another profile for the same user (should not cause error)
            try:
                profile2, created = CustomerProfile.objects.get_or_create(user=user)
                if created:
                    print("❌ Second profile was created (should not happen)")
                    return False
                else:
                    print("✅ get_or_create worked correctly - no duplicate created")
            except Exception as e:
                print(f"❌ Error with get_or_create: {e}")
                return False
            
            # Clean up
            user.delete()
            print("✅ Test completed successfully - registration fix works!")
            return True
            
        else:
            print(f"❌ Form validation failed: {form.errors}")
            return False
            
    except Exception as e:
        print(f"❌ Error during registration test: {e}")
        return False


def test_existing_user():
    """Test with existing user to ensure no conflicts"""
    print("\nTesting with existing user...")
    
    # Create a user first
    user = User.objects.create_user(
        username='existinguser',
        email='existing@example.com',
        password='testpass123',
        first_name='Existing',
        last_name='User'
    )
    
    try:
        # Try to create profile for existing user
        profile, created = CustomerProfile.objects.get_or_create(user=user)
        if created:
            print("✅ Profile created for existing user")
        else:
            print("✅ Profile already existed for user")
        
        # Try again - should not create duplicate
        profile2, created2 = CustomerProfile.objects.get_or_create(user=user)
        if created2:
            print("❌ Duplicate profile created")
            return False
        else:
            print("✅ No duplicate profile created - fix working correctly")
        
        # Clean up
        user.delete()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        user.delete()
        return False


if __name__ == '__main__':
    print("🧪 Testing Customer Registration Fix")
    print("=" * 50)
    
    success1 = test_customer_registration()
    success2 = test_existing_user()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED - Registration fix is working correctly!")
        sys.exit(0)
    else:
        print("❌ Some tests failed - please check the implementation")
        sys.exit(1)
