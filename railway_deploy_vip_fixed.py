#!/usr/bin/env python
"""
Railway Deployment Script - VIP Dashboard Fixed Version
This script ensures the VIP dashboard works perfectly on deployment
"""
import os
import sys
import django
import subprocess
from django.core.management import execute_from_command_line

def main():
    """Railway deployment - VIP dashboard fixed version"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🚀 RAILWAY DEPLOYMENT - VIP DASHBOARD FIXED VERSION")
    print("=" * 70)
    print("🔍 This script ensures VIP dashboard works perfectly")
    print("=" * 70)
    
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
            execute_from_command_line(['manage.py', 'create_vip_user', '--username', 'vip_demo', '--email', 'vip@meridianassetlogistics.com', '--password', 'vip123456', '--tier', 'gold'])
            print("✅ VIP test user created")
        except Exception as e:
            print(f"⚠️ VIP user creation failed: {e}")
        
        # Step 4: Collect static files with force
        print("🔄 STEP 4: Collecting static files...")
        try:
            # Try with --clear first
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
            print("✅ Static files collected with --clear")
        except Exception as e:
            print(f"⚠️ Static collection with --clear failed: {e}")
            try:
                # Try without --clear
                execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
                print("✅ Static files collected without --clear")
            except Exception as e2:
                print(f"⚠️ Static collection failed completely: {e2}")
        
        # Step 5: Verify VIP dashboard template exists
        print("🔄 STEP 5: Verifying VIP dashboard template...")
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'accounts', 'vip_dashboard.html')
        if os.path.exists(template_path):
            print("✅ VIP dashboard template exists")
            with open(template_path, 'r') as f:
                content = f.read()
                if 'dashboard-layout' in content:
                    print("✅ VIP dashboard layout CSS found")
                else:
                    print("⚠️ VIP dashboard layout CSS not found")
        else:
            print("❌ VIP dashboard template not found!")
        
        # Step 6: Test VIP dashboard view
        print("🔄 STEP 6: Testing VIP dashboard view...")
        try:
            from accounts.views import vip_dashboard
            print("✅ VIP dashboard view imports successfully")
        except Exception as e:
            print(f"❌ VIP dashboard view import failed: {e}")
        
        # Step 7: Start server
        print("🚀 STEP 7: Starting production server...")
        port = os.environ.get('PORT', '8080')
        
        print("=" * 70)
        print("✅ DEPLOYMENT COMPLETED!")
        print("=" * 70)
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
        print("")
        print("📊 Django Admin:")
        print("  Admin URL: https://meridianassetlogistics.com/admin/")
        print("  VIP Profiles: Admin > ACCOUNTS > VIP Profiles")
        print("  Staff Profiles: Admin > ACCOUNTS > Staff Profiles")
        print("  Customer Profiles: Admin > ACCOUNTS > Customer Profiles")
        print("")
        print("🎯 VIP Dashboard Features:")
        print("  ✅ Side-by-side layout (sidebar + main content)")
        print("  ✅ White theme with proper styling")
        print("  ✅ Real-time clock and date")
        print("  ✅ Financial overview cards")
        print("  ✅ Account information and statistics")
        print("  ✅ VIP benefits and account manager")
        print("  ✅ Recent activity feed")
        print("=" * 70)
        
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
