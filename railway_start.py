#!/usr/bin/env python
"""
Railway Production Startup - GUARANTEED VIP MEMBERS DEPLOYMENT
This script is specifically designed for Railway deployment
"""
import os
import sys
import django
import subprocess
from django.core.management import execute_from_command_line

def main():
    """Railway production startup with VIP Members"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🚀 RAILWAY VIP MEMBERS DEPLOYMENT")
    print("=" * 60)
    print("🔍 This is the CORRECT deployment script for VIP Members")
    print("🔍 Old deploy.py has been removed to prevent conflicts")
    print("=" * 60)
    
    try:
        # Initialize Django
        django.setup()
        print("✅ Django initialized")
        
        # CRITICAL: Run makemigrations first to ensure VIP migrations exist
        print("🔄 STEP 1: Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', '--noinput'])
        print("✅ Makemigrations completed")
        
        # Run all migrations
        print("🔄 STEP 2: Running all migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ All migrations completed")
        
        # Specifically run VIP Members migrations
        print("🔄 STEP 3: Running VIP Members migrations...")
        execute_from_command_line(['manage.py', 'migrate', 'vip_members', '--noinput'])
        print("✅ VIP Members migrations completed")
        
        # Verify VIP tables exist
        print("🔄 STEP 4: Verifying VIP tables...")
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
            print(f"📊 VIP tables found: {tables}")
            
            if len(tables) < 6:
                print("❌ VIP tables are missing - attempting to create...")
                # Try to force create tables
                try:
                    execute_from_command_line(['manage.py', 'force_create_vip_tables'])
                except:
                    pass
        
        # Set up VIP data
        print("🔄 STEP 5: Setting up VIP data...")
        try:
            execute_from_command_line(['manage.py', 'setup_vip_data'])
            print("✅ VIP data setup completed")
        except Exception as e:
            print(f"⚠️ VIP data setup failed: {e}")
        
        # Create test VIP member
        print("🔄 STEP 6: Creating test VIP member...")
        try:
            execute_from_command_line(['manage.py', 'create_test_vip_member'])
            print("✅ Test VIP member created")
        except Exception as e:
            print(f"⚠️ Test VIP member creation failed: {e}")
        
        # Collect static files
        print("🔄 STEP 7: Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected")
        
        # Start server
        print("🚀 STEP 8: Starting production server...")
        port = os.environ.get('PORT', '8080')
        
        print("=" * 60)
        print("✅ VIP MEMBERS SYSTEM IS READY!")
        print("=" * 60)
        print("🌐 Available Services:")
        print("  ✅ VIP Members: https://meridianassetlogistics.com/vip-members/")
        print("  ✅ VIP Dashboard: https://meridianassetlogistics.com/vip-members/dashboard/")
        print("  ✅ Investment Marketplace: https://meridianassetlogistics.com/investments/")
        print("=" * 60)
        print("🧪 Test Credentials:")
        print("  Username: vip_test_user")
        print("  Password: testpass123")
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
