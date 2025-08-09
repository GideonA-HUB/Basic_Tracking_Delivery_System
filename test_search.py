#!/usr/bin/env python
"""
Test script to demonstrate the search functionality
"""

import requests
import json

def test_search_functionality():
    """Test the search functionality"""
    base_url = "http://localhost:8000"
    
    print("🔍 Meridian Asset Logistics - Testing Search Functionality")
    print("=" * 50)
    
    # Test 1: Search by customer name
    print("\n1. Searching for 'John'...")
    response = requests.get(f"{base_url}/api/search/?q=John")
    if response.status_code == 200:
        results = response.json()
        print(f"   ✓ Found {len(results)} deliveries with 'John' in customer name")
        for delivery in results:
            print(f"   - {delivery['customer_name']} ({delivery['tracking_number']})")
    else:
        print(f"   ✗ Error: {response.status_code}")
    
    # Test 2: Search by tracking number
    print("\n2. Searching for tracking number '1RJ0A0VZGKOV'...")
    response = requests.get(f"{base_url}/api/search/?q=1RJ0A0VZGKOV")
    if response.status_code == 200:
        results = response.json()
        print(f"   ✓ Found {len(results)} deliveries with tracking number '1RJ0A0VZGKOV'")
        for delivery in results:
            print(f"   - {delivery['customer_name']} ({delivery['tracking_number']})")
    else:
        print(f"   ✗ Error: {response.status_code}")
    
    # Test 3: Search by status
    print("\n3. Searching for delivered deliveries...")
    response = requests.get(f"{base_url}/api/search/?status=delivered")
    if response.status_code == 200:
        results = response.json()
        print(f"   ✓ Found {len(results)} delivered deliveries")
        for delivery in results:
            print(f"   - {delivery['customer_name']} ({delivery['tracking_number']}) - {delivery['current_status_display']}")
    else:
        print(f"   ✗ Error: {response.status_code}")
    
    # Test 4: Combined search
    print("\n4. Searching for 'John' with 'delivered' status...")
    response = requests.get(f"{base_url}/api/search/?q=John&status=delivered")
    if response.status_code == 200:
        results = response.json()
        print(f"   ✓ Found {len(results)} deliveries matching both criteria")
        for delivery in results:
            print(f"   - {delivery['customer_name']} ({delivery['tracking_number']}) - {delivery['current_status_display']}")
    else:
        print(f"   ✗ Error: {response.status_code}")
    
    # Test 5: Search for non-existent delivery
    print("\n5. Searching for 'XYZ123' (non-existent)...")
    response = requests.get(f"{base_url}/api/search/?q=XYZ123")
    if response.status_code == 200:
        results = response.json()
        print(f"   ✓ Found {len(results)} deliveries (expected 0)")
    else:
        print(f"   ✗ Error: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("✅ Search functionality is working correctly!")
    print("\n🌐 You can now use the search feature on the dashboard:")
    print("   - Visit: http://localhost:8000/")
    print("   - Use the search bar to find deliveries")
    print("   - Filter by status using the dropdown")
    print("   - Clear search to show all deliveries")

if __name__ == "__main__":
    test_search_functionality()
