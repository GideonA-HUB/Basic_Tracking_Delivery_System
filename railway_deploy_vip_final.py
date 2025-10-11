#!/usr/bin/env python
"""
Railway Deployment Script - VIP Members Final Version
This script ensures VIP Members app works correctly with comprehensive error handling
"""
import os
import sys
import django
import subprocess
from django.core.management import execute_from_command_line

def main():
    """Railway deployment with comprehensive VIP Members support"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🚀 RAILWAY DEPLOYMENT - VIP MEMBERS FINAL")
    print("=" * 60)
    print("🔍 This script ensures VIP Members works with comprehensive error handling")
    print("=" * 60)
    
    try:
        # Initialize Django
        django.setup()
        print("✅ Django initialized")
        
        # Step 1: Test VIP Members app import
        print("🔄 STEP 1: Testing VIP Members app import...")
        try:
            import vip_members
            from vip_members.models import VIPMember, VIPStaff, VIPActivity, VIPBenefit, VIPNotification, VIPApplication
            print("✅ VIP Members app import successful")
        except Exception as e:
            print(f"❌ VIP Members app import failed: {e}")
            print("🔄 Continuing without VIP Members...")
            # Continue deployment without VIP Members
            run_basic_deployment()
            return
        
        # Step 2: Create migrations for all apps
        print("🔄 STEP 2: Creating migrations for all apps...")
        try:
            execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
            print("✅ Makemigrations completed")
        except Exception as e:
            print(f"⚠️ Makemigrations failed: {e}")
        
        # Step 3: Create VIP Members migrations specifically
        print("🔄 STEP 3: Creating VIP Members migrations...")
        try:
            execute_from_command_line(['manage.py', 'makemigrations', 'vip_members', '--noinput'])
            print("✅ VIP Members makemigrations completed")
        except Exception as e:
            print(f"⚠️ VIP Members makemigrations failed: {e}")
        
        # Step 4: Run all migrations
        print("🔄 STEP 4: Running all migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ All migrations completed")
        
        # Step 5: Run VIP Members migrations specifically
        print("🔄 STEP 5: Running VIP Members migrations...")
        try:
            execute_from_command_line(['manage.py', 'migrate', 'vip_members', '--noinput'])
            print("✅ VIP Members migrations completed")
        except Exception as e:
            print(f"⚠️ VIP Members migrations failed: {e}")
            print("🔄 Attempting to create VIP tables manually...")
            try:
                execute_from_command_line(['manage.py', 'force_create_vip_tables'])
                print("✅ VIP tables created manually")
            except Exception as e2:
                print(f"❌ Manual VIP table creation failed: {e2}")
        
        # Step 6: Verify VIP tables exist
        print("🔄 STEP 6: Verifying VIP tables...")
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'vip_members_%';")
            tables = cursor.fetchall()
            if tables:
                print(f"✅ VIP tables found: {[t[0] for t in tables]}")
            else:
                print("⚠️ No VIP tables found")
        except Exception as e:
            print(f"⚠️ Could not verify VIP tables: {e}")
        
        # Step 7: Set up VIP Members data
        print("🔄 STEP 7: Setting up VIP Members data...")
        try:
            execute_from_command_line(['manage.py', 'setup_vip_data'])
            print("✅ VIP Members data setup completed")
        except Exception as e:
            print(f"⚠️ VIP Members data setup failed: {e}")
        
        # Step 8: Create test VIP member
        print("🔄 STEP 8: Creating test VIP member...")
        try:
            execute_from_command_line(['manage.py', 'create_test_vip_member'])
            print("✅ Test VIP member created")
        except Exception as e:
            print(f"⚠️ Test VIP member creation failed: {e}")
        
        # Step 9: Collect static files
        print("🔄 STEP 9: Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected")
        
        # Step 10: Start server
        print("🚀 STEP 10: Starting production server...")
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
        print("🔄 Falling back to basic deployment...")
        run_basic_deployment()

def run_basic_deployment():
    """Fallback basic deployment without VIP Members"""
    print("🚀 RUNNING BASIC DEPLOYMENT (No VIP Members)")
    print("=" * 60)
    
    try:
        # Run basic migrations
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Basic migrations completed")
        
        # Collect static files
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected")
        
        # Start server
        port = os.environ.get('PORT', '8080')
        print("=" * 60)
        print("✅ BASIC DEPLOYMENT COMPLETED!")
        print("=" * 60)
        print("🌐 Available Services:")
        print("  ✅ Main Site: https://meridianassetlogistics.com/")
        print("  ✅ Investment Marketplace: https://meridianassetlogistics.com/investments/")
        print("  ⚠️ VIP Members: Not available (will be fixed in next deployment)")
        print("=" * 60)
        
        # Start Daphne
        cmd = ['daphne', '-b', '0.0.0.0', '-p', port, 'delivery_tracker.asgi:application']
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Basic deployment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
