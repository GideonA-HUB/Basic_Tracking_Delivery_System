#!/usr/bin/env python
"""
Script to add sample delivery data to PostgreSQL database
Run this after setting up PostgreSQL to populate the database with test data
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from tracking.models import Delivery, DeliveryStatus
from django.contrib.auth.models import User

def create_sample_deliveries():
    """Create sample deliveries with various statuses"""
    
    print("🚀 Adding sample data to PostgreSQL database...")
    print("=" * 60)
    
    # Sample customer data
    customers = [
        {"name": "John Smith", "email": "john.smith@email.com", "phone": "+1 (555) 123-4567"},
        {"name": "Sarah Johnson", "email": "sarah.j@email.com", "phone": "+1 (555) 234-5678"},
        {"name": "Michael Brown", "email": "michael.b@email.com", "phone": "+1 (555) 345-6789"},
        {"name": "Emily Davis", "email": "emily.d@email.com", "phone": "+1 (555) 456-7890"},
        {"name": "David Wilson", "email": "david.w@email.com", "phone": "+1 (555) 567-8901"},
        {"name": "Lisa Anderson", "email": "lisa.a@email.com", "phone": "+1 (555) 678-9012"},
        {"name": "Robert Taylor", "email": "robert.t@email.com", "phone": "+1 (555) 789-0123"},
        {"name": "Jennifer Martinez", "email": "jennifer.m@email.com", "phone": "+1 (555) 890-1234"},
        {"name": "Christopher Garcia", "email": "chris.g@email.com", "phone": "+1 (555) 901-2345"},
        {"name": "Amanda Rodriguez", "email": "amanda.r@email.com", "phone": "+1 (555) 012-3456"},
    ]
    
    # Sample package descriptions
    packages = [
        "Electronics package - Laptop and accessories",
        "Clothing shipment - Summer collection",
        "Home goods - Kitchen appliances",
        "Books and educational materials",
        "Sports equipment - Gym gear",
        "Medical supplies - First aid kit",
        "Office supplies - Stationery items",
        "Automotive parts - Engine components",
        "Jewelry - Precious metals and stones",
        "Food items - Organic groceries",
        "Furniture - Living room set",
        "Tools - Professional equipment",
        "Toys - Children's play items",
        "Art supplies - Painting materials",
        "Pet supplies - Animal care products",
    ]
    
    # Sample addresses
    addresses = [
        "123 Main Street, New York, NY 10001",
        "456 Oak Avenue, Los Angeles, CA 90210",
        "789 Pine Road, Chicago, IL 60601",
        "321 Elm Street, Houston, TX 77001",
        "654 Maple Drive, Phoenix, AZ 85001",
        "987 Cedar Lane, Philadelphia, PA 19101",
        "147 Birch Court, San Antonio, TX 78201",
        "258 Spruce Way, San Diego, CA 92101",
        "369 Willow Path, Dallas, TX 75201",
        "741 Aspen Circle, San Jose, CA 95101",
    ]
    
    # Status options
    statuses = ['pending', 'confirmed', 'in_transit', 'delivered']
    
    # Create deliveries
    deliveries_created = 0
    
    for i in range(1, 21):  # Create 20 sample deliveries
        customer = random.choice(customers)
        package = random.choice(packages)
        pickup = random.choice(addresses)
        delivery = random.choice(addresses)
        status = random.choice(statuses)
        
        # Create delivery
        delivery_obj = Delivery.objects.create(
            order_number=f"ORD-2024-{i:03d}",
            customer_name=customer["name"],
            customer_email=customer["email"],
            customer_phone=customer["phone"],
            pickup_address=pickup,
            delivery_address=delivery,
            package_description=package,
            package_weight=round(random.uniform(0.5, 25.0), 2),
            package_dimensions=f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)} cm",
            estimated_delivery=datetime.now() + timedelta(days=random.randint(1, 14)),
            current_status=status,
            created_by=User.objects.first()  # Use the first user (admin)
        )
        
        # Create status history
        status_history = []
        if status == 'pending':
            status_history = [
                ('pending', 'Order received and pending confirmation'),
            ]
        elif status == 'confirmed':
            status_history = [
                ('pending', 'Order received and pending confirmation'),
                ('confirmed', 'Order confirmed and ready for pickup'),
            ]
        elif status == 'in_transit':
            status_history = [
                ('pending', 'Order received and pending confirmation'),
                ('confirmed', 'Order confirmed and ready for pickup'),
                ('in_transit', 'Package picked up and in transit'),
            ]
        elif status == 'delivered':
            status_history = [
                ('pending', 'Order received and pending confirmation'),
                ('confirmed', 'Order confirmed and ready for pickup'),
                ('in_transit', 'Package picked up and in transit'),
                ('delivered', 'Package successfully delivered'),
            ]
        
        # Create status entries
        for status_code, description in status_history:
            DeliveryStatus.objects.create(
                delivery=delivery_obj,
                status=status_code,
                description=description,
                timestamp=datetime.now() - timedelta(days=len(status_history) - status_history.index((status_code, description)))
            )
        
        deliveries_created += 1
        print(f"✅ Created delivery {i:2d}: {customer['name']} - {status.upper()}")
    
    print("=" * 60)
    print(f"🎉 Successfully created {deliveries_created} sample deliveries!")
    print(f"📊 Database now contains {Delivery.objects.count()} total deliveries")
    
    # Show status breakdown
    print("\n📈 STATUS BREAKDOWN:")
    for status in statuses:
        count = Delivery.objects.filter(current_status=status).count()
        print(f"   {status.upper()}: {count} deliveries")
    
    print("\n🔗 You can now:")
    print("   - Visit http://localhost:8000/ to see the dashboard")
    print("   - Visit http://localhost:8000/admin/ to manage deliveries")
    print("   - Use tracking numbers to test the tracking system")

if __name__ == "__main__":
    try:
        create_sample_deliveries()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
