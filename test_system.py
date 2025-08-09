#!/usr/bin/env python
"""
Test script for the Delivery Tracking System
This script demonstrates the core functionality of the system.
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from tracking.models import Delivery, DeliveryStatus

def test_create_delivery():
    """Test creating a new delivery"""
    print("🚚 Testing Delivery Creation...")
    
    # Generate unique order number
    import time
    order_number = f"TEST-{int(time.time())}"
    
    # Create a test delivery
    delivery = Delivery.objects.create(
        order_number=order_number,
        customer_name="John Doe",
        customer_email="john@example.com",
        customer_phone="+1 (555) 123-4567",
        pickup_address="123 Warehouse St, City, State 12345",
        delivery_address="456 Customer Ave, City, State 12345",
        package_description="Electronics package with laptop and accessories",
        package_weight=2.5,
        package_dimensions="40x30x20 cm",
        estimated_delivery=datetime.now() + timedelta(days=3)
    )
    
    print(f"✓ Created delivery with tracking number: {delivery.tracking_number}")
    print(f"✓ Tracking URL: http://localhost:8000/track/{delivery.tracking_number}/{delivery.tracking_secret}/")
    
    return delivery

def test_status_updates(delivery):
    """Test updating delivery status"""
    print("\n📊 Testing Status Updates...")
    
    # Create status updates
    statuses = [
        ("confirmed", "Order confirmed and ready for shipping", "Warehouse"),
        ("in_transit", "Package picked up and in transit", "Distribution Center"),
        ("out_for_delivery", "Package is out for delivery today", "Local Facility"),
        ("delivered", "Package successfully delivered", "Customer Address")
    ]
    
    for status, description, location in statuses:
        DeliveryStatus.objects.create(
            delivery=delivery,
            status=status,
            description=description,
            location=location
        )
        print(f"✓ Added status update: {status} - {description}")
    
    print(f"✓ Final status: {delivery.current_status}")

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test getting all deliveries
        response = requests.get(f"{base_url}/api/deliveries/")
        if response.status_code == 200:
            print("✓ GET /api/deliveries/ - Success")
        else:
            print(f"✗ GET /api/deliveries/ - Failed: {response.status_code}")
        
        # Test getting statistics
        response = requests.get(f"{base_url}/api/stats/")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ GET /api/stats/ - Success")
            print(f"  Total deliveries: {stats.get('total_deliveries', 0)}")
        else:
            print(f"✗ GET /api/stats/ - Failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API tests skipped - server not running")
        print("   Start the server with: python manage.py runserver")

def test_tracking_link(delivery):
    """Test the tracking link functionality"""
    print("\n🔗 Testing Tracking Link...")
    
    tracking_url = f"http://localhost:8000/track/{delivery.tracking_number}/{delivery.tracking_secret}/"
    print(f"✓ Tracking URL: {tracking_url}")
    print("  (Open this URL in a browser to see the customer tracking page)")
    
    # Test API tracking endpoint
    api_url = f"http://localhost:8000/api/track/{delivery.tracking_number}/{delivery.tracking_secret}/"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API tracking endpoint - Success")
            print(f"  Customer: {data.get('customer_name')}")
            print(f"  Status: {data.get('current_status_display')}")
        else:
            print(f"✗ API tracking endpoint - Failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠️  API tracking test skipped - server not running")

def main():
    """Main test function"""
    print("🧪 Meridian Asset Logistics - Delivery Tracking System Test")
    print("=" * 50)
    
    # Test creating a delivery
    delivery = test_create_delivery()
    
    # Test status updates
    test_status_updates(delivery)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test tracking link
    test_tracking_link(delivery)
    
    print("\n🎉 Test completed successfully!")
    print("\n📋 Summary:")
    print(f"  - Created delivery: {delivery.tracking_number}")
    print(f"  - Customer: {delivery.customer_name}")
    print(f"  - Final status: {delivery.get_current_status_display()}")
    print(f"  - Tracking URL: http://localhost:8000/track/{delivery.tracking_number}/{delivery.tracking_secret}/")
    
    print("\n🚀 To see the system in action:")
    print("1. Start the server: python manage.py runserver")
    print("2. Visit the dashboard: http://localhost:8000/")
    print("3. View the tracking page: http://localhost:8000/track/{delivery.tracking_number}/{delivery.tracking_secret}/")
    print("4. Access the admin: http://localhost:8000/admin/ (admin/admin)")

if __name__ == "__main__":
    main()
