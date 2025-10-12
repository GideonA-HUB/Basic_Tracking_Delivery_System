#!/usr/bin/env python3
"""
VIP Dashboard Deployment Verification Script
This script verifies that the VIP dashboard is properly configured for deployment.
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def check_template_integrity():
    """Check VIP dashboard template integrity"""
    print("🔍 Checking VIP Dashboard Template Integrity...")
    
    template_path = "templates/accounts/vip_dashboard.html"
    
    if not check_file_exists(template_path, "VIP Dashboard Template"):
        return False
    
    # Read and check template content
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for essential Django template tags
        required_tags = [
            "{% extends 'base.html' %}",
            "{% block title %}",
            "{% block extra_css %}",
            "{% block content %}",
            "{% block extra_js %}"
        ]
        
        for tag in required_tags:
            if tag in content:
                print(f"✅ Found required template tag: {tag}")
            else:
                print(f"❌ Missing required template tag: {tag}")
                return False
        
        # Check for VIP-specific content
        vip_content = [
            "vip_member",
            "dashboard-layout",
            "balance-card",
            "MERIDIAN VIP"
        ]
        
        for content_item in vip_content:
            if content_item in content:
                print(f"✅ Found VIP content: {content_item}")
            else:
                print(f"⚠️  VIP content not found: {content_item}")
        
        # Check for Tailwind CSS classes
        tailwind_classes = [
            "bg-white",
            "dark:bg-gray-800",
            "rounded-xl",
            "grid",
            "flex"
        ]
        
        for css_class in tailwind_classes:
            if css_class in content:
                print(f"✅ Found Tailwind CSS class: {css_class}")
            else:
                print(f"⚠️  Tailwind CSS class not found: {css_class}")
        
        print("✅ VIP Dashboard template integrity check passed")
        return True
        
    except Exception as e:
        print(f"❌ Error reading template: {str(e)}")
        return False

def check_deployment_files():
    """Check deployment configuration files"""
    print("🚀 Checking Deployment Configuration...")
    
    deployment_files = [
        ("Procfile", "Procfile for deployment"),
        ("railway.json", "Railway deployment config"),
        ("requirements.txt", "Python dependencies"),
        ("runtime.txt", "Python runtime version")
    ]
    
    all_exist = True
    for file_path, description in deployment_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_django_configuration():
    """Check Django configuration for VIP dashboard"""
    print("⚙️  Checking Django Configuration...")
    
    try:
        # Check if Django settings are accessible
        sys.path.insert(0, '.')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Basic_Tracking_Delivery_System.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        
        # Check required settings
        required_settings = [
            'TEMPLATES',
            'STATIC_URL',
            'STATIC_ROOT',
            'MEDIA_URL',
            'MEDIA_ROOT'
        ]
        
        for setting in required_settings:
            if hasattr(settings, setting):
                print(f"✅ Django setting found: {setting}")
            else:
                print(f"❌ Django setting missing: {setting}")
                return False
        
        # Check if VIP models are accessible
        from accounts.models import VIPProfile, StaffProfile
        print("✅ VIP models are accessible")
        
        # Check if VIP views are accessible
        from accounts.views import vip_dashboard
        print("✅ VIP dashboard view is accessible")
        
        print("✅ Django configuration check passed")
        return True
        
    except Exception as e:
        print(f"❌ Django configuration check failed: {str(e)}")
        return False

def check_static_files():
    """Check static files configuration"""
    print("📁 Checking Static Files Configuration...")
    
    # Check if static files directory exists
    static_dirs = [
        "static",
        "staticfiles"
    ]
    
    for static_dir in static_dirs:
        if Path(static_dir).exists():
            print(f"✅ Static directory found: {static_dir}")
        else:
            print(f"⚠️  Static directory not found: {static_dir}")
    
    # Check for common static files
    static_files = [
        "static/css",
        "static/js",
        "static/images"
    ]
    
    for static_file in static_files:
        if Path(static_file).exists():
            print(f"✅ Static subdirectory found: {static_file}")
        else:
            print(f"⚠️  Static subdirectory not found: {static_file}")
    
    print("✅ Static files check completed")
    return True

def check_requirements():
    """Check Python requirements"""
    print("📦 Checking Python Requirements...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Check for essential packages
        essential_packages = [
            'Django',
            'djangorestframework',
            'psycopg2-binary',
            'gunicorn',
            'whitenoise'
        ]
        
        for package in essential_packages:
            if package in requirements:
                print(f"✅ Essential package found: {package}")
            else:
                print(f"❌ Essential package missing: {package}")
                return False
        
        print("✅ Requirements check passed")
        return True
        
    except Exception as e:
        print(f"❌ Requirements check failed: {str(e)}")
        return False

def main():
    """Main verification function"""
    print("🔍 VIP Dashboard Deployment Verification")
    print("=" * 60)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"📂 Working directory: {project_dir}")
    print()
    
    # Run all checks
    checks = [
        ("Template Integrity", check_template_integrity),
        ("Deployment Files", check_deployment_files),
        ("Django Configuration", check_django_configuration),
        ("Static Files", check_static_files),
        ("Requirements", check_requirements)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {str(e)}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{check_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED!")
        print("🚀 VIP Dashboard is ready for deployment!")
        print("\n📋 Deployment Checklist:")
        print("✅ VIP dashboard template is properly configured")
        print("✅ Django configuration is correct")
        print("✅ Deployment files are in place")
        print("✅ Static files are configured")
        print("✅ Python requirements are met")
        print("\n🔗 Ready to deploy to Railway!")
        return True
    else:
        print(f"\n❌ {total - passed} CHECK(S) FAILED!")
        print("🔧 Please fix the issues above before deploying.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
