#!/usr/bin/env python3
"""
Test script for VIP Dashboard functionality
This script tests the VIP dashboard template and ensures all components work correctly.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Basic_Tracking_Delivery_System.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from accounts.models import VIPProfile, StaffProfile
from accounts.views import vip_dashboard

def test_vip_dashboard():
    """Test the VIP dashboard view and template"""
    print("🧪 Testing VIP Dashboard...")
    
    try:
        # Create test data
        print("📝 Creating test data...")
        
        # Create a test user
        user = User.objects.create_user(
            username='testvip',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        # Create a staff member for assignment
        staff_user = User.objects.create_user(
            username='staff1',
            email='staff@example.com',
            password='staffpass123',
            first_name='Jane',
            last_name='Smith',
            is_staff=True
        )
        
        staff_profile = StaffProfile.objects.create(
            user=staff_user,
            role='customer_care',
            department='VIP Services'
        )
        
        # Create VIP profile
        vip_profile = VIPProfile.objects.create(
            user=user,
            member_id='VIP-TEST001',
            membership_tier='gold',
            status='active',
            assigned_staff=staff_profile,
            total_investments=125000.00,
            monthly_income=15000.00,
            net_worth=500000.00
        )
        
        print("✅ Test data created successfully")
        
        # Test the view
        print("🔍 Testing VIP dashboard view...")
        
        factory = RequestFactory()
        request = factory.get('/accounts/vip/dashboard/')
        request.user = user
        
        response = vip_dashboard(request)
        
        if response.status_code == 200:
            print("✅ VIP dashboard view returns 200 OK")
        else:
            print(f"❌ VIP dashboard view returned {response.status_code}")
            return False
            
        # Test template rendering
        print("🎨 Testing template rendering...")
        
        if 'vip_dashboard.html' in response.template_name:
            print("✅ Correct template is being used")
        else:
            print("❌ Wrong template being used")
            return False
            
        # Test context data
        print("📊 Testing context data...")
        
        context = response.context_data
        if 'vip_member' in context:
            print("✅ VIP member data is in context")
        else:
            print("❌ VIP member data missing from context")
            return False
            
        if 'assigned_staff' in context:
            print("✅ Assigned staff data is in context")
        else:
            print("❌ Assigned staff data missing from context")
            return False
            
        # Test VIP profile data
        vip_member = context['vip_member']
        if vip_member.full_name == 'John Doe':
            print("✅ VIP member name is correct")
        else:
            print(f"❌ VIP member name incorrect: {vip_member.full_name}")
            return False
            
        if vip_member.member_id == 'VIP-TEST001':
            print("✅ VIP member ID is correct")
        else:
            print(f"❌ VIP member ID incorrect: {vip_member.member_id}")
            return False
            
        print("🎉 All VIP dashboard tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up test data
        print("🧹 Cleaning up test data...")
        try:
            User.objects.filter(username__in=['testvip', 'staff1']).delete()
            VIPProfile.objects.filter(member_id='VIP-TEST001').delete()
            StaffProfile.objects.filter(user__username='staff1').delete()
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up test data: {str(e)}")

def test_template_syntax():
    """Test Django template syntax"""
    print("🔧 Testing template syntax...")
    
    try:
        from django.template import Template, Context
        from django.template.loader import get_template
        
        # Test loading the template
        template = get_template('accounts/vip_dashboard.html')
        print("✅ Template loads successfully")
        
        # Test basic template rendering with minimal context
        context = Context({
            'vip_member': type('MockVIP', (), {
                'full_name': 'Test User',
                'member_id': 'VIP-123',
                'get_membership_tier_display': lambda: 'Gold',
                'get_status_display': lambda: 'Active',
                'membership_start_date': type('MockDate', (), {
                    'date': lambda fmt: 'Jan 2024'
                })(),
                'total_investments': 100000,
                'monthly_income': 10000,
                'net_worth': 500000
            })(),
            'user': type('MockUser', (), {
                'first_name': 'Test',
                'last_name': 'User'
            })(),
            'assigned_staff': None
        })
        
        rendered = template.render(context)
        
        if len(rendered) > 1000:  # Basic check that template rendered content
            print("✅ Template renders successfully")
        else:
            print("❌ Template rendering failed or returned minimal content")
            return False
            
        print("🎉 Template syntax tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Template syntax test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Starting VIP Dashboard Tests...")
    print("=" * 50)
    
    # Run tests
    template_test = test_template_syntax()
    dashboard_test = test_vip_dashboard()
    
    print("=" * 50)
    if template_test and dashboard_test:
        print("🎉 ALL TESTS PASSED! VIP Dashboard is ready for deployment.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED! Please check the issues above.")
        sys.exit(1)
