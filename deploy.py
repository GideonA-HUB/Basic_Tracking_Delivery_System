#!/usr/bin/env python
"""
Railway deployment script for Meridian Asset Logistics
"""

import os
import sys
import subprocess

def main():
    """Deploy the application to Railway"""
    
    # Set environment variables for production
    os.environ['DJANGO_SETTINGS_MODULE'] = 'delivery_tracker.settings_production'
    os.environ['DEBUG'] = 'False'
    
    print("🚀 Starting Railway deployment for Meridian Asset Logistics")
    print("=" * 60)
    
    try:
        # Import Django
        import django
        from django.core.management import execute_from_command_line
        from django.conf import settings
        
        # Initialize Django
        django.setup()
        print("✅ Django initialized with production settings")
        
        # Show current settings
        print(f"📋 Settings: {settings.DJANGO_SETTINGS_MODULE}")
        print(f"📋 Debug: {settings.DEBUG}")
        print(f"📋 Allowed Hosts: {settings.ALLOWED_HOSTS}")
        
        # Run migrations
        print("\n🔄 Running database migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations completed successfully")
        
        # Collect static files
        print("\n📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected successfully")
        
        # Start the server
        print("\n🌐 Starting production server...")
        port = os.environ.get('PORT', '8080')
        
        # Use gunicorn for production
        cmd = [
            'gunicorn',
            'delivery_tracker.wsgi:application',
            f'--bind=0.0.0.0:{port}',
            '--workers=3',
            '--timeout=120',
            '--keep-alive=2',
            '--max-requests=1000',
            '--max-requests-jitter=100'
        ]
        
        print(f"🚀 Starting server on port {port}")
        print(f"📝 Command: {' '.join(cmd)}")
        
        # Start the server
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
