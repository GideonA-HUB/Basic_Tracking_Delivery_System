#!/usr/bin/env python
"""
Daphne startup script for Railway deployment with proper port handling
"""

import os
import sys
import subprocess

def main():
    """Start the application with Daphne ASGI server"""
    try:
        # Set Django settings module
        os.environ['DJANGO_SETTINGS_MODULE'] = 'delivery_tracker.settings'
        print(f"✅ Django settings module set to: {os.environ['DJANGO_SETTINGS_MODULE']}")
        
        # Get port from environment (Railway provides this)
        port = os.environ.get('PORT', '8080')
        print(f"✅ Using port: {port}")
        
        # Debug environment variables
        print(f"🔍 PORT: {os.environ.get('PORT', 'Not set')}")
        print(f"🔍 REDIS_URL: {os.environ.get('REDIS_URL', 'Not set')}")
        
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
            print(f"⚠️ Migration failed: {migate_error}")
            print("🔄 Continuing without migrations...")
        
        # Collect static files
        print("📁 Collecting static files...")
        try:
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
            print("✅ Static files collected successfully")
        except Exception as static_error:
            print(f"⚠️ Static files collection failed: {static_error}")
            print("🔄 Continuing without static files...")
        
        # Start Daphne ASGI server
        print(f"🚀 Starting Daphne ASGI server on port {port}...")
        
        daphne_cmd = [
            'daphne',
            '-b', '0.0.0.0',
            '-p', port,
            '--access-log', '-',
            '--proxy-headers',
            'delivery_tracker.asgi:application'
        ]
        
        print(f"🔧 Running: {' '.join(daphne_cmd)}")
        subprocess.run(daphne_cmd)
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
