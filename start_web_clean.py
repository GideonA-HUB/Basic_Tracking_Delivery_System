#!/usr/bin/env python
"""
Clean web server startup script for Railway deployment
"""

import os
import sys

def main():
    """Start the web application"""
    try:
        # Clear any existing Django settings
        if 'DJANGO_SETTINGS_MODULE' in os.environ:
            del os.environ['DJANGO_SETTINGS_MODULE']
        
        # Set Django settings module to regular settings
        os.environ['DJANGO_SETTINGS_MODULE'] = 'delivery_tracker.settings'
        
        print(f"✅ Django settings module set to: {os.environ['DJANGO_SETTINGS_MODULE']}")
        
        # Import Django after setting the environment
        import django
        from django.core.management import execute_from_command_line
        
        # Initialize Django
        django.setup()
        print("✅ Django initialized successfully")
        
        # Run migrations
        print("🔄 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        # Collect static files
        print("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        # Start the server
        print("🚀 Starting web server...")
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
