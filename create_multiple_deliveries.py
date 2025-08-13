#!/usr/bin/env python
"""
Script to create multiple deliveries with different statuses for testing.
Run this script to populate the database with sample delivery data.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from tracking.models import Delivery, DeliveryStatus
from django.contrib.auth.models import User

def create_deliveries():
    """Create multiple deliveries with different statuses"""
    
    # Sample customer data
    customers = [
        {
            'name': 'John Smith',
            'email': 'john.smith@email.com',
            'phone': '+1-555-0101',
            'pickup': '123 Main St, New York, NY 10001',
            'delivery': '456 Oak Ave, Brooklyn, NY 11201',
            'description': 'Electronics package - Laptop and accessories'
        },
        {
            'name': 'Sarah Johnson',
            'email': 'sarah.j@email.com',
            'phone': '+1-555-0102',
            'pickup': '789 Business Blvd, Los Angeles, CA 90210',
            'delivery': '321 Home St, San Francisco, CA 94102',
            'description': 'Fragile items - Glass vases and ceramics'
        },
        {
            'name': 'Michael Brown',
            'email': 'mike.brown@email.com',
            'phone': '+1-555-0103',
            'pickup': '555 Warehouse Dr, Chicago, IL 60601',
            'delivery': '777 Residential Rd, Detroit, MI 48201',
            'description': 'Heavy machinery parts - Industrial equipment'
        },
        {
            'name': 'Emily Davis',
            'email': 'emily.davis@email.com',
            'phone': '+1-555-0104',
            'pickup': '888 Shopping Center, Miami, FL 33101',
            'delivery': '999 Beach Blvd, Orlando, FL 32801',
            'description': 'Clothing and accessories - Fashion items'
        },
        {
            'name': 'David Wilson',
            'email': 'david.wilson@email.com',
            'phone': '+1-555-0105',
            'pickup': '444 Office Park, Seattle, WA 98101',
            'delivery': '666 Tech Ave, Portland, OR 97201',
            'description': 'Computer hardware - Servers and networking equipment'
        },
        {
            'name': 'Lisa Anderson',
            'email': 'lisa.anderson@email.com',
            'phone': '+1-555-0106',
            'pickup': '222 Industrial Zone, Houston, TX 77001',
            'delivery': '333 Suburban Ln, Austin, TX 73301',
            'description': 'Medical supplies - Pharmaceuticals and equipment'
        },
        {
            'name': 'Robert Taylor',
            'email': 'robert.taylor@email.com',
            'phone': '+1-555-0107',
            'pickup': '111 Downtown Plaza, Phoenix, AZ 85001',
            'delivery': '222 Desert Rd, Las Vegas, NV 89101',
            'description': 'Sports equipment - Golf clubs and accessories'
        },
        {
            'name': 'Jennifer Martinez',
            'email': 'jen.martinez@email.com',
            'phone': '+1-555-0108',
            'pickup': '777 Mall Complex, Denver, CO 80201',
            'delivery': '888 Mountain View, Salt Lake City, UT 84101',
            'description': 'Outdoor gear - Camping and hiking equipment'
        }
    ]
    
    # Status progression with locations
    status_data = [
        {
            'status': 'pending',
            'location': 'Origin Warehouse',
            'description': 'Order received and pending confirmation'
        },
        {
            'status': 'confirmed',
            'location': 'Processing Center',
            'description': 'Order confirmed and being prepared for shipment'
        },
        {
            'status': 'in_transit',
            'location': 'Distribution Hub',
            'description': 'Package in transit to destination'
        },
        {
            'status': 'in_transit',
            'location': 'Local Facility',
            'description': 'Package arrived at local delivery facility'
        },
        {
            'status': 'delivered',
            'location': 'Customer Address',
            'description': 'Package successfully delivered to recipient'
        }
    ]
    
    # Get or create a staff user for creating deliveries
    try:
        staff_user = User.objects.filter(is_staff=True).first()
        if not staff_user:
            staff_user = User.objects.create_user(
                username='staff_user',
                email='staff@example.com',
                password='staffpass123',
                is_staff=True
            )
    except Exception as e:
        print(f"Error creating staff user: {e}")
        return
    
    print("Creating deliveries...")
    
    # Create deliveries with different statuses
    for i, customer in enumerate(customers):
        # Determine status based on index
        if i < 2:  # First 2 deliveries: pending
            current_status = 'pending'
            status_index = 0
        elif i < 4:  # Next 2 deliveries: confirmed
            current_status = 'confirmed'
            status_index = 1
        elif i < 6:  # Next 2 deliveries: in_transit
            current_status = 'in_transit'
            status_index = 2
        else:  # Last 2 deliveries: delivered
            current_status = 'delivered'
            status_index = 4
        
        # Create delivery
        delivery = Delivery.objects.create(
            order_number=f"ORD-{2025:04d}-{i+1:04d}",
            customer_name=customer['name'],
            customer_email=customer['email'],
            customer_phone=customer['phone'],
            pickup_address=customer['pickup'],
            delivery_address=customer['delivery'],
            package_description=customer['description'],
            package_weight=random.uniform(1.0, 25.0),
            package_dimensions=f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)} cm",
            estimated_delivery=datetime.now() + timedelta(days=random.randint(1, 7)),
            current_status=current_status,
            created_by=staff_user
        )
        
        # Create status updates based on current status
        for j in range(status_index + 1):
            status_info = status_data[j]
            created_time = datetime.now() - timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
            
            DeliveryStatus.objects.create(
                delivery=delivery,
                status=status_info['status'],
                location=status_info['location'],
                description=status_info['description'],
                created_at=created_time
            )
        
        print(f"✅ Created delivery for {customer['name']} - Status: {current_status}")
        print(f"   Tracking Number: {delivery.tracking_number}")
        print(f"   Order Number: {delivery.order_number}")
        print()
    
    print("🎉 All deliveries created successfully!")
    print(f"📊 Summary:")
    print(f"   - Pending: 2 deliveries")
    print(f"   - Confirmed: 2 deliveries")
    print(f"   - In Transit: 2 deliveries")
    print(f"   - Delivered: 2 deliveries")
    print(f"   - Total: 8 deliveries")

if __name__ == '__main__':
    create_deliveries()
