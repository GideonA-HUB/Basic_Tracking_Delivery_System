#!/usr/bin/env python
"""
VIP Dashboard Deployment Verification Script
This script verifies that the VIP dashboard is properly deployed and working
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.test import Client
from django.contrib.auth.models import User
from accounts.models import VIPProfile

def main():
    """Verify VIP dashboard deployment"""
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
    
    print("🔍 VIP DASHBOARD DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    try:
        # Initialize Django
        django.setup()
        print("✅ Django initialized")
        
        # Step 1: Check if VIP user exists
        print("🔄 STEP 1: Checking VIP user...")
        try:
            vip_user = User.objects.get(username='vip_demo')
            print(f"✅ VIP user found: {vip_user.username}")
            
            # Check VIP profile
            vip_profile = VIPProfile.objects.get(user=vip_user)
            print(f"✅ VIP profile found: {vip_profile.member_id}")
            print(f"✅ VIP tier: {vip_profile.get_membership_tier_display()}")
            print(f"✅ VIP status: {vip_profile.get_status_display()}")
            
        except User.DoesNotExist:
            print("❌ VIP user not found!")
            return False
        except VIPProfile.DoesNotExist:
            print("❌ VIP profile not found!")
            return False
        
        # Step 2: Check VIP dashboard template
        print("🔄 STEP 2: Checking VIP dashboard template...")
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'accounts', 'vip_dashboard.html')
        if os.path.exists(template_path):
            print("✅ VIP dashboard template exists")
            with open(template_path, 'r') as f:
                content = f.read()
                if 'dashboard-layout' in content:
                    print("✅ Dashboard layout CSS found")
                else:
                    print("⚠️ Dashboard layout CSS not found")
                
                if 'CRITICAL OVERRIDE' in content:
                    print("✅ Critical CSS overrides found")
                else:
                    print("⚠️ Critical CSS overrides not found")
                
                if 'grid-template-columns: 280px 1fr' in content:
                    print("✅ Side-by-side layout CSS found")
                else:
                    print("⚠️ Side-by-side layout CSS not found")
        else:
            print("❌ VIP dashboard template not found!")
            return False
        
        # Step 3: Test VIP dashboard view
        print("🔄 STEP 3: Testing VIP dashboard view...")
        try:
            from accounts.views import vip_dashboard
            print("✅ VIP dashboard view imports successfully")
        except Exception as e:
            print(f"❌ VIP dashboard view import failed: {e}")
            return False
        
        # Step 4: Test VIP dashboard URL
        print("🔄 STEP 4: Testing VIP dashboard URL...")
        try:
            client = Client()
            # Login as VIP user
            login_success = client.login(username='vip_demo', password='vip123456')
            if login_success:
                print("✅ VIP user login successful")
                
                # Test VIP dashboard access
                response = client.get('/accounts/vip/dashboard/')
                if response.status_code == 200:
                    print("✅ VIP dashboard accessible")
                    
                    # Check if template content is correct
                    if 'dashboard-layout' in response.content.decode():
                        print("✅ Dashboard layout HTML found in response")
                    else:
                        print("⚠️ Dashboard layout HTML not found in response")
                    
                    if 'grid-template-columns' in response.content.decode():
                        print("✅ Grid layout CSS found in response")
                    else:
                        print("⚠️ Grid layout CSS not found in response")
                        
                else:
                    print(f"❌ VIP dashboard not accessible: {response.status_code}")
                    return False
            else:
                print("❌ VIP user login failed")
                return False
        except Exception as e:
            print(f"❌ VIP dashboard URL test failed: {e}")
            return False
        
        # Step 5: Check static files
        print("🔄 STEP 5: Checking static files...")
        static_root = os.path.join(os.path.dirname(__file__), 'staticfiles')
        if os.path.exists(static_root):
            print("✅ Static files directory exists")
        else:
            print("⚠️ Static files directory not found")
        
        print("=" * 60)
        print("✅ VIP DASHBOARD DEPLOYMENT VERIFICATION COMPLETE!")
        print("=" * 60)
        print("🎯 VIP Dashboard Status: WORKING")
        print("🌐 Access URL: https://meridianassetlogistics.com/accounts/vip/dashboard/")
        print("🔑 Login Credentials:")
        print("   Username: vip_demo")
        print("   Password: vip123456")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)