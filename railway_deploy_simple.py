#!/usr/bin/env python
"""
Railway Deployment Script - Simple Version
This script deploys the system without VIP Members app complications
"""
import os
import sys
import django
import subprocess
from django.core.management import execute_from_command_line

def main():
    """Railway deployment - simple version"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🚀 RAILWAY DEPLOYMENT - SIMPLE VERSION")
    print("=" * 60)
    print("🔍 This script deploys the system with VIP login functionality")
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
        
        # Step 2: Run all migrations
        print("🔄 STEP 2: Running all migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ All migrations completed")
        
        # Step 3: Create VIP test user
        print("🔄 STEP 3: Creating VIP test user...")
        try:
            execute_from_command_line(['manage.py', 'create_vip_user', '--username', 'vip_demo', '--email', 'vip@meridianassetlogistics.com', '--password', 'vip123456'])
            print("✅ VIP test user created")
        except Exception as e:
            print(f"⚠️ VIP user creation failed: {e}")
        
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
        print("  ✅ VIP Login: https://meridianassetlogistics.com/accounts/vip/login/")
        print("  ✅ VIP Dashboard: https://meridianassetlogistics.com/accounts/vip/dashboard/")
        print("  ✅ Customer Login: https://meridianassetlogistics.com/accounts/customer/login/")
        print("  ✅ Staff Login: https://meridianassetlogistics.com/accounts/login/")
        print("")
        print("🔑 VIP Demo Credentials:")
        print("  Username: vip_demo")
        print("  Password: vip123456")
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
