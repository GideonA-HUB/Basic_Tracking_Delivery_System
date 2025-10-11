#!/usr/bin/env python
"""
VIP Members Production Deployment Fix
This script ensures VIP Members system is properly deployed to production
"""
import os
import sys
import django
import subprocess
from django.core.management import execute_from_command_line

def run_vip_migrations():
    """Run VIP Members migrations specifically"""
    try:
        print("🔄 Running VIP Members migrations...")
        
        # Run all migrations first
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ All migrations completed")
        
        # Specifically ensure VIP Members migrations
        execute_from_command_line(['manage.py', 'migrate', 'vip_members', '--noinput'])
        print("✅ VIP Members migrations completed")
        
        return True
    except Exception as e:
        print(f"❌ VIP Members migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def setup_vip_data():
    """Set up initial VIP data"""
    try:
        print("🔄 Setting up VIP data...")
        execute_from_command_line(['manage.py', 'setup_vip_data'])
        print("✅ VIP data setup completed")
        return True
    except Exception as e:
        print(f"⚠️ VIP data setup failed: {e}")
        # Don't fail the deployment if this fails
        return False

def create_test_vip_member():
    """Create test VIP member for demonstration"""
    try:
        print("🔄 Creating test VIP member...")
        execute_from_command_line(['manage.py', 'create_test_vip_member'])
        print("✅ Test VIP member created")
        return True
    except Exception as e:
        print(f"⚠️ Test VIP member creation failed: {e}")
        # Don't fail the deployment if this fails
        return False

def verify_vip_tables():
    """Verify VIP tables exist"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Check if VIP tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'vip_members_%'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            expected_tables = [
                'vip_members_vipbenefit',
                'vip_members_vipmember', 
                'vip_members_vipstaff',
                'vip_members_vipactivity',
                'vip_members_vipnotification',
                'vip_members_vipapplication'
            ]
            
            existing_tables = [table[0] for table in tables]
            
            print(f"📊 Found {len(existing_tables)} VIP tables:")
            for table in existing_tables:
                print(f"  ✅ {table}")
            
            missing_tables = [table for table in expected_tables if table not in existing_tables]
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                return False
            else:
                print("✅ All VIP tables exist")
                return True
                
    except Exception as e:
        print(f"❌ Error verifying VIP tables: {e}")
        return False

def main():
    """Main deployment function"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🚀 VIP MEMBERS PRODUCTION DEPLOYMENT FIX")
    print("=" * 60)
    
    try:
        # Initialize Django
        django.setup()
        print("✅ Django initialized")
        
        # Run migrations
        if not run_vip_migrations():
            print("❌ Migration failed - deployment cannot continue")
            sys.exit(1)
        
        # Verify tables exist
        if not verify_vip_tables():
            print("❌ VIP tables verification failed")
            sys.exit(1)
        
        # Set up VIP data
        setup_vip_data()
        
        # Create test VIP member
        create_test_vip_member()
        
        # Collect static files
        print("📁 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected")
        
        # Start the server
        print("🚀 Starting production server...")
        
        # Get port from environment
        port = os.environ.get('PORT', '8080')
        
        # Start Daphne
        cmd = [
            'daphne', 
            '-b', '0.0.0.0', 
            '-p', port, 
            'delivery_tracker.asgi:application'
        ]
        
        print(f"🚀 Starting server on port {port}")
        print("✅ VIP Members system is ready!")
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Error during VIP deployment: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
