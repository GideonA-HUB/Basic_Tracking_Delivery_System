#!/usr/bin/env python
"""
Static files collection script for Railway deployment
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    # Setup Django
    django.setup()
    
    print("🚨 COLLECTING STATIC FILES...")
    
    try:
        # Collect static files
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected successfully")
        
        # Verify critical files
        static_root = os.path.join(os.getcwd(), 'staticfiles')
        critical_files = [
            'js/live_price_dashboard.js',
            'js/delivery_tracking_map.js',
            'js/test_static.js'
        ]
        
        for file_path in critical_files:
            full_path = os.path.join(static_root, file_path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"✅ {file_path} exists ({size} bytes)")
            else:
                print(f"❌ {file_path} missing")
                
    except Exception as e:
        print(f"❌ Static files collection failed: {e}")
        sys.exit(1)
