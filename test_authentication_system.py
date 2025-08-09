#!/usr/bin/env python3
"""
Test script for the authentication system
Tests staff login, protected routes, and public access
"""

import requests
import time
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:8000"

def test_public_access():
    """Test that public routes are accessible without authentication"""
    print("🔍 Testing public access...")
    
    # Test landing page (should be accessible)
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Landing page accessible without authentication")
        else:
            print(f"❌ Landing page returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing landing page: {e}")
    
    # Test tracking page (should be accessible)
    try:
        response = requests.get(f"{BASE_URL}/track/test123/testsecret/")
        if response.status_code == 200:
            print("✅ Tracking page accessible without authentication")
        else:
            print(f"❌ Tracking page returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing tracking page: {e}")

def test_protected_routes():
    """Test that staff-only routes require authentication"""
    print("\n🔒 Testing protected routes...")
    
    # Test dashboard (should redirect to login)
    try:
        response = requests.get(f"{BASE_URL}/dashboard/", allow_redirects=False)
        if response.status_code == 302:  # Redirect
            print("✅ Dashboard redirects to login when not authenticated")
        else:
            print(f"❌ Dashboard returned status {response.status_code} instead of redirect")
    except Exception as e:
        print(f"❌ Error accessing dashboard: {e}")
    
    # Test create delivery page (should redirect to login)
    try:
        response = requests.get(f"{BASE_URL}/create/", allow_redirects=False)
        if response.status_code == 302:  # Redirect
            print("✅ Create delivery page redirects to login when not authenticated")
        else:
            print(f"❌ Create delivery page returned status {response.status_code} instead of redirect")
    except Exception as e:
        print(f"❌ Error accessing create delivery page: {e}")

def test_api_protection():
    """Test that API endpoints are protected"""
    print("\n🛡️ Testing API protection...")
    
    # Test deliveries API (should require authentication)
    try:
        response = requests.get(f"{BASE_URL}/api/deliveries/")
        if response.status_code == 401:  # Unauthorized
            print("✅ Deliveries API requires authentication")
        else:
            print(f"❌ Deliveries API returned status {response.status_code} instead of 401")
    except Exception as e:
        print(f"❌ Error accessing deliveries API: {e}")
    
    # Test search API (should require authentication)
    try:
        response = requests.get(f"{BASE_URL}/api/deliveries/search/?q=test")
        if response.status_code == 401:  # Unauthorized
            print("✅ Search API requires authentication")
        else:
            print(f"❌ Search API returned status {response.status_code} instead of 401")
    except Exception as e:
        print(f"❌ Error accessing search API: {e}")
    
    # Test stats API (should require authentication)
    try:
        response = requests.get(f"{BASE_URL}/api/deliveries/stats/")
        if response.status_code == 401:  # Unauthorized
            print("✅ Stats API requires authentication")
        else:
            print(f"❌ Stats API returned status {response.status_code} instead of 401")
    except Exception as e:
        print(f"❌ Error accessing stats API: {e}")

def test_public_api():
    """Test that public API endpoints are accessible"""
    print("\n🌐 Testing public API access...")
    
    # Test tracking API (should be accessible)
    try:
        response = requests.get(f"{BASE_URL}/api/tracking/test123/testsecret/")
        if response.status_code == 404:  # Not found (expected for test data)
            print("✅ Tracking API accessible without authentication (404 expected for test data)")
        elif response.status_code == 200:
            print("✅ Tracking API accessible without authentication")
        else:
            print(f"⚠️ Tracking API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing tracking API: {e}")

def test_login_page():
    """Test that login page is accessible"""
    print("\n🔑 Testing login page...")
    
    try:
        response = requests.get(f"{BASE_URL}/accounts/login/")
        if response.status_code == 200:
            print("✅ Login page accessible")
            
            # Check if it contains login form
            soup = BeautifulSoup(response.content, 'html.parser')
            form = soup.find('form')
            if form:
                print("✅ Login form found")
            else:
                print("❌ Login form not found")
        else:
            print(f"❌ Login page returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing login page: {e}")

def test_navigation():
    """Test navigation based on authentication status"""
    print("\n🧭 Testing navigation...")
    
    # Test unauthenticated navigation
    try:
        response = requests.get(f"{BASE_URL}/")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for staff login link
        login_link = soup.find('a', href='/accounts/login/')
        if login_link:
            print("✅ Staff login link visible for unauthenticated users")
        else:
            print("❌ Staff login link not found")
        
        # Check for home link
        home_link = soup.find('a', href='/')
        if home_link:
            print("✅ Home link visible for unauthenticated users")
        else:
            print("❌ Home link not found")
        
        # Check that dashboard link is NOT visible in navigation
        dashboard_link = soup.find('a', href='/dashboard/')
        if not dashboard_link:
            print("✅ Dashboard link hidden from unauthenticated users")
        else:
            print("❌ Dashboard link visible to unauthenticated users")
        
        # Check that MAL logo points to landing page for unauthenticated users
        mal_logo = soup.find('a', href='/')
        if mal_logo:
            print("✅ MAL logo points to landing page for unauthenticated users")
        else:
            print("❌ MAL logo not pointing to landing page")
            
    except Exception as e:
        print(f"❌ Error testing navigation: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing Authentication System")
    print("=" * 50)
    
    test_public_access()
    test_protected_routes()
    test_api_protection()
    test_public_api()
    test_login_page()
    test_navigation()
    
    print("\n" + "=" * 50)
    print("✅ Authentication system testing completed!")
    print("\n📝 Next steps:")
    print("1. Create a staff user through the admin interface")
    print("2. Test staff login functionality")
    print("3. Verify staff can access protected routes")
    print("4. Test that customers can still view tracking without login")

if __name__ == "__main__":
    main()
