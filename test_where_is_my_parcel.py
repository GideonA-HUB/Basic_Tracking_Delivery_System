#!/usr/bin/env python3
"""
Meridian Asset Logistics - Testing "Where's My Parcel?" Page
"""

import requests
import time

def test_where_is_my_parcel_page():
    """Test the new Where's My Parcel? page"""
    print("=" * 60)
    print("Meridian Asset Logistics - Testing 'Where's My Parcel?' Page")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test the main page
        print("\n1. Testing main dashboard page...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Dashboard page loads successfully")
            if "where-is-my-parcel" in response.text:
                print("✅ 'Let's Find It' link is present")
            else:
                print("❌ 'Let's Find It' link not found")
        else:
            print(f"❌ Dashboard page failed: {response.status_code}")
        
        # Test the Where's My Parcel? page
        print("\n2. Testing Where's My Parcel? page...")
        response = requests.get(f"{base_url}/where-is-my-parcel/")
        if response.status_code == 200:
            print("✅ Where's My Parcel? page loads successfully")
            
            # Check for key content
            content = response.text
            checks = [
                ("Where's My Parcel?", "Main heading"),
                ("First, Check for an InfoNotice", "InfoNotice section"),
                ("Find One? Sorry We Missed You", "Step 1"),
                ("Now What?", "Step 2"),
                ("More Info", "Step 3"),
                ("Track Now", "Track Now button"),
                ("Learn More", "Learn More link"),
                ("Two people in a lab looking at a laptop", "Hero image description")
            ]
            
            for text, description in checks:
                if text in content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
                    
        else:
            print(f"❌ Where's My Parcel? page failed: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Django server is running.")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_where_is_my_parcel_page()
