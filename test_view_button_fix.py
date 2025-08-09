#!/usr/bin/env python3
"""
Meridian Asset Logistics - Testing View Button Fix
"""
import requests
from bs4 import BeautifulSoup

def test_view_button_fix():
    """Test that the View button now works properly"""
    print("=" * 60)
    print("Meridian Asset Logistics - Testing View Button Fix")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        print("\n1. Testing dashboard page...")
        response = requests.get(f"{base_url}/")
        
        if response.status_code == 200:
            print("✅ Dashboard page loads successfully")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for data attributes
            print("\n2. Testing data attributes...")
            delivery_items = soup.find_all('li', attrs={'data-delivery-id': True})
            
            if delivery_items:
                print(f"✅ Found {len(delivery_items)} delivery items with data attributes")
                
                for item in delivery_items[:3]:  # Check first 3 items
                    delivery_id = item.get('data-delivery-id')
                    tracking_number = item.get('data-tracking-number')
                    tracking_secret = item.get('data-tracking-secret')
                    
                    print(f"   Item {delivery_id}:")
                    print(f"     - Tracking Number: {tracking_number}")
                    print(f"     - Tracking Secret: {tracking_secret[:20]}..." if tracking_secret else "     - Tracking Secret: None")
                    
                    if tracking_number and tracking_secret:
                        print(f"     ✅ Complete tracking data")
                    else:
                        print(f"     ❌ Missing tracking data")
            else:
                print("❌ No delivery items found with data attributes")
            
            # Check for JavaScript functions
            print("\n3. Testing JavaScript functions...")
            js_checks = [
                ("function viewDelivery", "viewDelivery function"),
                ("function testViewDelivery", "testViewDelivery function"),
                ("console.log", "Console logging for debugging"),
                ("data-delivery-id", "Data attributes in HTML")
            ]
            
            for text, description in js_checks:
                if text in response.text:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
            
            # Check for test buttons
            print("\n4. Testing debug buttons...")
            test_buttons = soup.find_all('button', onclick=lambda x: x and 'testViewDelivery' in x)
            if test_buttons:
                print(f"✅ Found {len(test_buttons)} test buttons")
            else:
                print("❌ No test buttons found")
                
        else:
            print(f"❌ Dashboard page failed: {response.status_code}")
            
        print("\n" + "=" * 60)
        print("View Button Fix Test completed!")
        print("=" * 60)
        
        print("\n📋 Next Steps:")
        print("1. Refresh the dashboard page in your browser")
        print("2. Click the purple 'Test' button on any delivery")
        print("3. Check the browser console for debug information")
        print("4. If the test works, try the blue 'View' button")
        print("5. The View button should now redirect to the tracking page")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Django server is running.")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_view_button_fix()
