#!/usr/bin/env python
"""
Production web server startup script for Railway deployment
"""

import os
import sys
import subprocess

def main():
    """Start the web application in production mode"""
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
        
        # Run migrations first
        print("🔄 Running migrations...")
        try:
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
        
        # Start the server using Gunicorn (production server)
        print("🚀 Starting production web server with Gunicorn...")
        
        # Use Gunicorn for production
        gunicorn_cmd = [
            'gunicorn',
            '--bind', '0.0.0.0:8000',
            '--workers', '3',
            '--timeout', '120',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--preload',
            '--access-logfile', '-',
            '--error-logfile', '-',
            'delivery_tracker.wsgi:application'
        ]
        
        print(f"🔧 Running: {' '.join(gunicorn_cmd)}")
        subprocess.run(gunicorn_cmd)
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
