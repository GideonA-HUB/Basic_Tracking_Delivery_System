#!/usr/bin/env python
"""
VIP Members Only Deployment Fix
This script ONLY fixes the VIP Members system
"""
import os
import sys
import django
import subprocess
from django.core.management import execute_from_command_line

def main():
    """Main deployment function - VIP Members only"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🚀 VIP MEMBERS DEPLOYMENT FIX")
    print("=" * 50)
    
    try:
        # Initialize Django
        django.setup()
        print("✅ Django initialized")
        
        # Force create VIP tables
        print("🔄 Force creating VIP tables...")
        execute_from_command_line(['manage.py', 'force_create_vip_tables'])
        print("✅ VIP tables creation completed")
        
        # Set up VIP data
        print("🔄 Setting up VIP data...")
        execute_from_command_line(['manage.py', 'setup_vip_data'])
        print("✅ VIP data setup completed")
        
        # Create test VIP member
        print("🔄 Creating test VIP member...")
        execute_from_command_line(['manage.py', 'create_test_vip_member'])
        print("✅ Test VIP member created")
        
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
        print("✅ Test login: vip_test_user / testpass123")
        print("✅ VIP Dashboard: /vip-members/dashboard/")
        
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Error during VIP deployment: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
