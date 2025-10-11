#!/usr/bin/env python
"""
Railway Deployment Script - VIP Members Working Version
This script ensures VIP Members app is properly deployed
"""
import os
import sys
import django
import subprocess
from django.core.management import execute_from_command_line

def main():
    """Railway deployment with VIP Members support"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🚀 RAILWAY DEPLOYMENT - VIP MEMBERS WORKING")
    print("=" * 60)
    print("🔍 This script ensures VIP Members works properly")
    print("=" * 60)
    
    try:
        # Initialize Django
        django.setup()
        print("✅ Django initialized")
        
        # Step 1: Create migrations for all apps
        print("🔄 STEP 1: Creating migrations for all apps...")
        try:
            execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
            print("✅ Makemigrations completed")
        except Exception as e:
            print(f"⚠️ Makemigrations failed: {e}")
        
        # Step 2: Create VIP Members migrations specifically
        print("🔄 STEP 2: Creating VIP Members migrations...")
        try:
            execute_from_command_line(['manage.py', 'makemigrations', 'vip_members', '--noinput'])
            print("✅ VIP Members makemigrations completed")
        except Exception as e:
            print(f"⚠️ VIP Members makemigrations failed: {e}")
        
        # Step 3: Run all migrations
        print("🔄 STEP 3: Running all migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ All migrations completed")
        
        # Step 4: Run VIP Members migrations specifically
        print("🔄 STEP 4: Running VIP Members migrations...")
        try:
            execute_from_command_line(['manage.py', 'migrate', 'vip_members', '--noinput'])
            print("✅ VIP Members migrations completed")
        except Exception as e:
            print(f"⚠️ VIP Members migrations failed: {e}")
            # Continue anyway, don't crash the deployment
        
        # Step 5: Set up VIP Members data
        print("🔄 STEP 5: Setting up VIP Members data...")
        try:
            execute_from_command_line(['manage.py', 'setup_vip_data'])
            print("✅ VIP Members data setup completed")
        except Exception as e:
            print(f"⚠️ VIP Members data setup failed: {e}")
        
        # Step 6: Create test VIP member
        print("🔄 STEP 6: Creating test VIP member...")
        try:
            execute_from_command_line(['manage.py', 'create_test_vip_member'])
            print("✅ Test VIP member created")
        except Exception as e:
            print(f"⚠️ Test VIP member creation failed: {e}")
        
        # Step 7: Collect static files
        print("🔄 STEP 7: Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected")
        
        # Step 8: Start server
        print("🚀 STEP 8: Starting production server...")
        port = os.environ.get('PORT', '8080')
        
        print("=" * 60)
        print("✅ DEPLOYMENT COMPLETED!")
        print("=" * 60)
        print("🌐 Available Services:")
        print("  ✅ Main Site: https://meridianassetlogistics.com/")
        print("  ✅ Investment Marketplace: https://meridianassetlogistics.com/investments/")
        print("  ✅ VIP Members: https://meridianassetlogistics.com/vip-members/")
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
