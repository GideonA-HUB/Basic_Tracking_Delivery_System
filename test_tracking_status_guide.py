#!/usr/bin/env python3
"""
Meridian Asset Logistics - Testing "What Does My Tracking Status Mean?" Page
"""

import requests
import time

def test_tracking_status_guide():
    """Test the new Tracking Status Guide page"""
    print("=" * 60)
    print("Meridian Asset Logistics - Testing 'What Does My Tracking Status Mean?' Page")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test the main page
        print("\n1. Testing main dashboard page...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Dashboard page loads successfully")
            if "tracking-status-guide" in response.text:
                print("✅ 'We will tell you' link is present")
            else:
                print("❌ 'We will tell you' link not found")
        else:
            print(f"❌ Dashboard page failed: {response.status_code}")
        
        # Test the Tracking Status Guide page
        print("\n2. Testing Tracking Status Guide page...")
        response = requests.get(f"{base_url}/tracking-status-guide/")
        if response.status_code == 200:
            print("✅ Tracking Status Guide page loads successfully")
            
            # Check for key content
            content = response.text
            checks = [
                ("What Does My Tracking Status Mean?", "Main heading"),
                ("Each time your parcel is scanned", "Introduction text"),
                ("Label Created", "Status 1"),
                ("Shipped/On the Way", "Status 2"),
                ("Out for Delivery", "Status 3"),
                ("Delivered", "Status 4"),
                ("Delivered to a Meridian Asset Logistics Access Point", "Status 5"),
                ("Exception", "Status 6"),
                ("Can't Find What You're Looking For?", "Call to action"),
                ("Contact Meridian Asset Logistics", "Contact button"),
                ("Common Tracking Statuses", "Status list heading")
            ]
            
            for text, description in checks:
                if text in content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
                    
        else:
            print(f"❌ Tracking Status Guide page failed: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Django server is running.")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_tracking_status_guide()
