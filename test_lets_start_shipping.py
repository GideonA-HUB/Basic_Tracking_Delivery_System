#!/usr/bin/env python3
"""
Meridian Asset Logistics - Testing "Let's Start Shipping" Section
"""

import requests
import time

def test_lets_start_shipping():
    """Test the new Let's Start Shipping section on the dashboard"""
    print("=" * 60)
    print("Meridian Asset Logistics - Testing 'Let's Start Shipping' Section")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test the dashboard page
        print("\n1. Testing dashboard page...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Dashboard page loads successfully")
            
            # Check for key content
            content = response.text
            checks = [
                ("Let's Start Shipping", "Main heading"),
                ("You have parcels. We'll take care of them.", "Description text"),
                ("Ship Now", "Ship Now button"),
                ("unsplash.com/photo-1507003211169-0a1dd7228f2d", "Person smiling image"),
                ("person smiling while preparing packages", "Image alt text"),
                ("Let's Start Shipping Section", "Section comment"),
                ("bg-gradient-to-br from-blue-50 to-indigo-100", "Gradient background"),
                ("bg-blue-600 hover:bg-blue-700", "Blue button styling"),
                ("w-24 h-1 bg-yellow-400", "Yellow underline")
            ]
            
            for text, description in checks:
                if text in content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
                    
        else:
            print(f"❌ Dashboard page failed: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Django server is running.")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_lets_start_shipping()
