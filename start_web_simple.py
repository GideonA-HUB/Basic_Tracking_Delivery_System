#!/usr/bin/env python
"""
Simple web server startup script for Railway deployment
"""

import os
import sys

def main():
    """Start the web application"""
    try:
        # Set Django settings module
        os.environ['DJANGO_SETTINGS_MODULE'] = 'delivery_tracker.settings'
        print(f"✅ Django settings module set to: {os.environ['DJANGO_SETTINGS_MODULE']}")
        
        # Import Django
        import django
        from django.core.management import execute_from_command_line
        
        # Initialize Django
        django.setup()
        print("✅ Django initialized successfully")
        
        # Start the server directly
        print("🚀 Starting web server...")
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
