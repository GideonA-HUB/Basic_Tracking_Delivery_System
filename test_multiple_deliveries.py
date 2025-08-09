#!/usr/bin/env python
"""
Test script to demonstrate multiple deliveries with unique tracking links
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from tracking.models import Delivery

def create_multiple_deliveries():
    """Create multiple deliveries to show unique tracking links"""
    print("🚚 Meridian Asset Logistics - Creating Multiple Deliveries with Unique Tracking Links")
    print("=" * 60)
    
    # Sample delivery data
    deliveries_data = [
        {
            "customer_name": "Alice Johnson",
            "customer_email": "alice@example.com",
            "customer_phone": "+1 (555) 111-1111",
            "pickup_address": "123 Warehouse St, City, State 12345",
            "delivery_address": "456 Alice Ave, City, State 12345",
            "package_description": "Electronics package with laptop",
            "package_weight": 2.5,
            "package_dimensions": "40x30x20 cm",
        },
        {
            "customer_name": "Bob Smith",
            "customer_email": "bob@example.com",
            "customer_phone": "+1 (555) 222-2222",
            "pickup_address": "789 Distribution Center, City, State 12345",
            "delivery_address": "321 Bob Street, City, State 12345",
            "package_description": "Clothing package with winter coats",
            "package_weight": 1.8,
            "package_dimensions": "50x40x15 cm",
        },
        {
            "customer_name": "Carol Davis",
            "customer_email": "carol@example.com",
            "customer_phone": "+1 (555) 333-3333",
            "pickup_address": "456 Logistics Hub, City, State 12345",
            "delivery_address": "654 Carol Road, City, State 12345",
            "package_description": "Books and educational materials",
            "package_weight": 3.2,
            "package_dimensions": "60x45x25 cm",
        }
    ]
    
    created_deliveries = []
    
    for i, data in enumerate(deliveries_data, 1):
        # Generate unique order number
        import time
        order_number = f"ORDER-{int(time.time())}-{i}"
        
        # Create delivery
        delivery = Delivery.objects.create(
            order_number=order_number,
            estimated_delivery=datetime.now() + timedelta(days=3),
            **data
        )
        
        created_deliveries.append(delivery)
        
        print(f"\n📦 Delivery {i}: {delivery.customer_name}")
        print(f"   Order Number: {delivery.order_number}")
        print(f"   Tracking Number: {delivery.tracking_number}")
        print(f"   Tracking Secret: {delivery.tracking_secret[:20]}...")
        print(f"   Tracking URL: http://localhost:8000/track/{delivery.tracking_number}/{delivery.tracking_secret}/")
        print(f"   Expires: {delivery.tracking_link_expires.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 60)
    print("✅ Each delivery has its own unique tracking link!")
    print("\n🔍 Key Points:")
    print("   • Each delivery gets a unique tracking_number")
    print("   • Each delivery gets a unique tracking_secret")
    print("   • Each delivery gets its own tracking URL")
    print("   • Each delivery has its own expiry date")
    print("   • No two deliveries share the same tracking link")
    
    return created_deliveries

if __name__ == "__main__":
    create_multiple_deliveries()
