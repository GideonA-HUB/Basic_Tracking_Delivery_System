#!/usr/bin/env python
"""
Simple web server startup script for Railway deployment
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Start the web application"""
    try:
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
        
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
        sys.exit(1)

if __name__ == '__main__':
    main()
