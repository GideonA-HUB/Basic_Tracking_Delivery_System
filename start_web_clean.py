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
        
        # Check database connection first
        print("🔍 Checking database connection...")
        from django.db import connection
        try:
            connection.ensure_connection()
            print("✅ Database connection successful")
        except Exception as db_error:
            print(f"❌ Database connection failed: {db_error}")
            print("🔄 Skipping migrations due to database connection issue")
            # Continue without migrations for now
        
        # Run migrations only if database is connected
        try:
            print("🔄 Running migrations...")
            execute_from_command_line(['manage.py', 'migrate', '--noinput'])
            print("✅ Migrations completed successfully")
        except Exception as migrate_error:
            print(f"⚠️ Migration failed: {migrate_error}")
            print("🔄 Continuing without migrations...")
        
        # Collect static files
        print("📁 Collecting static files...")
        try:
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
            print("✅ Static files collected successfully")
        except Exception as static_error:
            print(f"⚠️ Static files collection failed: {static_error}")
            print("🔄 Continuing without static files...")
        
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
