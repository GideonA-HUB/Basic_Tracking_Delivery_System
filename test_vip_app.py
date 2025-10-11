#!/usr/bin/env python
"""
Test script to verify VIP Members app can be imported
"""
import os
import sys
import django

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')

try:
    django.setup()
    print("✅ Django setup successful")
    
    # Try to import VIP Members app
    try:
        from vip_members.models import VIPMember, VIPStaff, VIPBenefit
        print("✅ VIP Members models imported successfully")
        
        # Try to get app config
        from django.apps import apps
        vip_app = apps.get_app_config('vip_members')
        print(f"✅ VIP Members app found: {vip_app.name}")
        print(f"✅ VIP Members app label: {vip_app.label}")
        
    except Exception as e:
        print(f"❌ VIP Members import failed: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
