#!/usr/bin/env python
"""
Railway Deployment Script - Working Version
This script focuses on getting the basic deployment working without VIP Members
"""
import os
import sys
import django
import subprocess
from django.core.management import execute_from_command_line

def main():
    """Railway deployment - working version"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🚀 RAILWAY DEPLOYMENT - WORKING VERSION")
    print("=" * 60)
    print("🔍 This script focuses on basic deployment first")
    print("=" * 60)
    
    try:
        # Initialize Django
        django.setup()
        print("✅ Django initialized")
        
        # Step 1: Run makemigrations for all apps
        print("🔄 STEP 1: Creating migrations for all apps...")
        try:
            execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
            print("✅ Makemigrations completed")
        except Exception as e:
            print(f"⚠️ Makemigrations failed: {e}")
        
        # Step 2: Run all migrations
        print("🔄 STEP 2: Running all migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ All migrations completed")
        
        # Step 3: Skip VIP Members for now
        print("🔄 STEP 3: Skipping VIP Members for now...")
        print("⚠️ VIP Members will be set up later")
        
        # Step 4: Collect static files
        print("🔄 STEP 4: Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected")
        
        # Step 5: Start server
        print("🚀 STEP 5: Starting production server...")
        port = os.environ.get('PORT', '8080')
        
        print("=" * 60)
        print("✅ DEPLOYMENT COMPLETED!")
        print("=" * 60)
        print("🌐 Available Services:")
        print("  ✅ Main Site: https://meridianassetlogistics.com/")
        print("  ✅ Investment Marketplace: https://meridianassetlogistics.com/investments/")
        print("  ⚠️ VIP Members: Will be added in next deployment")
        print("=" * 60)
        
        # Start Daphne
        cmd = ['daphne', '-b', '0.0.0.0', '-p', port, 'delivery_tracker.asgi:application']
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
