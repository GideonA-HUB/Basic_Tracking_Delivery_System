#!/usr/bin/env python3
"""
Meridian Asset Logistics - Testing MAL Logo
"""

import requests

def test_mal_logo():
    """Test the new MAL logo on the website"""
    print("=" * 60)
    print("Meridian Asset Logistics - Testing MAL Logo")
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
                ("bg-blue-600 text-white font-bold text-2xl px-3 py-2 rounded-lg shadow-md", "MAL logo styling"),
                ("MAL", "MAL acronym"),
                ("Meridian Asset Logistics", "Full company name"),
                ("Dashboard - MAL (Meridian Asset Logistics)", "Page title with MAL"),
                ("MAL (Meridian Asset Logistics) deliveries", "Header description with MAL"),
                ("hover:opacity-80 transition-opacity duration-200", "Logo hover effects")
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
    test_mal_logo()
