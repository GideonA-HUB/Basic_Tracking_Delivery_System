#!/usr/bin/env python
"""
Test VIP Dashboard Locally
This script tests the VIP dashboard functionality locally
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Test VIP dashboard locally"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🧪 TESTING VIP DASHBOARD LOCALLY")
    print("=" * 50)
    
    try:
        # Initialize Django
        django.setup()
        print("✅ Django initialized")
        
        # Create VIP user if it doesn't exist
        print("🔄 Creating VIP test user...")
        try:
            execute_from_command_line(['manage.py', 'create_vip_user', '--username', 'test_vip', '--email', 'test@meridianassetlogistics.com', '--password', 'test123456', '--tier', 'gold'])
            print("✅ VIP test user created")
        except Exception as e:
            print(f"⚠️ VIP user creation failed: {e}")
        
        # Run migrations
        print("🔄 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations completed")
        
        # Collect static files
        print("🔄 Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected")
        
        # Start development server
        print("🚀 Starting development server...")
        print("=" * 50)
        print("🌐 Local URLs:")
        print("  ✅ Main Site: http://localhost:8000/")
        print("  ✅ VIP Login: http://localhost:8000/accounts/vip/login/")
        print("  ✅ VIP Dashboard: http://localhost:8000/accounts/vip/dashboard/")
        print("")
        print("🔑 Test Credentials:")
        print("  Username: test_vip")
        print("  Password: test123456")
        print("=" * 50)
        
        # Start server
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()