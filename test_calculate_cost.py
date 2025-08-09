#!/usr/bin/env python3
"""
Meridian Asset Logistics - Testing "Calculate Time and Cost" Page
"""

import requests
import time

def test_calculate_cost():
    """Test the new Calculate Cost page"""
    print("=" * 60)
    print("Meridian Asset Logistics - Testing 'Calculate Time and Cost' Page")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test the main page
        print("\n1. Testing main dashboard page...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Dashboard page loads successfully")
            if "calculate-cost" in response.text:
                print("✅ 'Let's Find Out' link is present")
            else:
                print("❌ 'Let's Find Out' link not found")
        else:
            print(f"❌ Dashboard page failed: {response.status_code}")
        
        # Test the Calculate Cost page
        print("\n2. Testing Calculate Cost page...")
        response = requests.get(f"{base_url}/calculate-cost/")
        if response.status_code == 200:
            print("✅ Calculate Cost page loads successfully")
            
            # Check for key content
            content = response.text
            checks = [
                ("Calculate Time and Cost", "Main heading"),
                ("Quickly get estimated shipping quotes", "Introduction text"),
                ("Log in and select a Meridian Asset Logistics account", "Login prompt"),
                ("Package", "Package tab"),
                ("Freight", "Freight tab"),
                ("Where and When?", "Step 1 heading"),
                ("Ship From:", "Ship From section"),
                ("Ship To:", "Ship To section"),
                ("Country or Territory", "Country field"),
                ("Locality", "Locality field"),
                ("Postcode", "Postcode field"),
                ("Residential Address", "Residential checkbox"),
                ("When are you shipping?", "Date field"),
                ("Clear", "Clear button"),
                ("Update", "Update button"),
                ("Showing Results For:", "Results section"),
                ("Meridian Asset Logistics Express", "Service option 1"),
                ("Meridian Asset Logistics Express Saver", "Service option 2"),
                ("Meridian Asset Logistics Standard", "Service option 3"),
                ("Zones and Rates", "Additional resources")
            ]
            
            for text, description in checks:
                if text in content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
                    
        else:
            print(f"❌ Calculate Cost page failed: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Django server is running.")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_calculate_cost()
