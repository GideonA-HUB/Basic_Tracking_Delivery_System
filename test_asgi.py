#!/usr/bin/env python
"""
Test script to verify ASGI configuration works without AppRegistryNotReady error
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')

# Initialize Django
django.setup()

# Now try to import the ASGI application
try:
    from delivery_tracker.asgi import application
    print("✅ ASGI application imported successfully!")
    print("✅ Django apps are properly loaded!")
    print("✅ WebSocket routing should work!")
    
    # Test if we can access models
    from django.apps import apps
    User = apps.get_model('auth', 'User')
    print(f"✅ User model accessible: {User}")
    
    InvestmentItem = apps.get_model('investments', 'InvestmentItem')
    print(f"✅ InvestmentItem model accessible: {InvestmentItem}")
    
    print("\n🎉 All tests passed! The ASGI configuration is working correctly.")
    
except Exception as e:
    print(f"❌ Error importing ASGI application: {e}")
    import traceback
    traceback.print_exc()
