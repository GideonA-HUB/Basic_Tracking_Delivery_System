#!/usr/bin/env python
"""
Deployment Verification Script
This script verifies that the new VIP dashboard design is properly deployed
"""
import os
import sys
import django

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

def verify_vip_dashboard():
    """Verify VIP dashboard deployment"""
    print("🔍 VERIFYING VIP DASHBOARD DEPLOYMENT")
    print("=" * 50)
    
    # Check if template exists
    template_path = "templates/accounts/vip_dashboard.html"
    if os.path.exists(template_path):
        print(f"✅ Template exists: {template_path}")
        
        # Check template content
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "NEW DESIGN DEPLOYED" in content:
            print("✅ New design banner found in template")
        else:
            print("❌ New design banner NOT found in template")
            
        if "v2.0.0 - New Design" in content:
            print("✅ Version indicator found in template")
        else:
            print("❌ Version indicator NOT found in template")
            
        if "Silver Bridge Bank Inspired Design" in content:
            print("✅ Silver Bridge design styles found")
        else:
            print("❌ Silver Bridge design styles NOT found")
            
    else:
        print(f"❌ Template NOT found: {template_path}")
    
    # Check VIP profile model
    try:
        from accounts.models import VIPProfile
        print("✅ VIP Profile model imported successfully")
        
        # Check if any VIP profiles exist
        vip_count = VIPProfile.objects.count()
        print(f"📊 VIP Profiles in database: {vip_count}")
        
        if vip_count > 0:
            vip = VIPProfile.objects.first()
            print(f"📊 Sample VIP Profile: {vip.user.username} - {vip.member_id}")
        
    except Exception as e:
        print(f"❌ VIP Profile model error: {e}")
    
    # Check VIP views
    try:
        from accounts.views import vip_dashboard, is_vip_user
        print("✅ VIP dashboard views imported successfully")
    except Exception as e:
        print(f"❌ VIP dashboard views error: {e}")
    
    print("=" * 50)
    print("🎯 DEPLOYMENT VERIFICATION COMPLETE")
    print("=" * 50)

if __name__ == '__main__':
    verify_vip_dashboard()
