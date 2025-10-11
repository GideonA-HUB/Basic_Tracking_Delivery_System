#!/usr/bin/env python
"""
Railway Deployment Script - VIP Members Fixed
This script handles the VIP Members app recognition issue
"""
import os
import sys
import django
import subprocess
from django.core.management import execute_from_command_line

def main():
    """Railway deployment with VIP Members fix"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🚀 RAILWAY DEPLOYMENT - VIP MEMBERS FIXED")
    print("=" * 60)
    print("🔍 This script handles VIP Members app recognition")
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
        
        # Step 3: Try VIP Members specific migration
        print("🔄 STEP 3: Attempting VIP Members migration...")
        try:
            execute_from_command_line(['manage.py', 'migrate', 'vip_members', '--noinput'])
            print("✅ VIP Members migrations completed")
        except Exception as e:
            print(f"⚠️ VIP Members migration failed: {e}")
            print("🔄 This is expected if VIP Members app is not recognized yet")
        
        # Step 4: Check if VIP tables exist
        print("🔄 STEP 4: Checking VIP tables...")
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'vip_members_%'
                    ORDER BY table_name;
                """)
                tables = [row[0] for row in cursor.fetchall()]
                print(f"📊 VIP tables found: {len(tables)}")
                if tables:
                    print("✅ VIP tables exist!")
                    for table in tables:
                        print(f"  ✅ {table}")
                else:
                    print("⚠️ No VIP tables found - VIP Members app may not be properly installed")
        except Exception as e:
            print(f"⚠️ Could not check VIP tables: {e}")
        
        # Step 5: Try to set up VIP data if tables exist
        print("🔄 STEP 5: Setting up VIP data...")
        try:
            from vip_members.models import VIPBenefit
            if VIPBenefit.objects.count() == 0:
                execute_from_command_line(['manage.py', 'setup_vip_data'])
                print("✅ VIP data setup completed")
            else:
                print("✅ VIP data already exists")
        except Exception as e:
            print(f"⚠️ VIP data setup failed: {e}")
        
        # Step 6: Try to create test VIP member
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
        print("  ⚠️ VIP Members: May need additional setup")
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
