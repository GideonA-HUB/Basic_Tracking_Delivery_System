#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from tracking.models import Delivery, DeliveryStatus
from django.contrib.auth.models import User

def add_sample_deliveries():
    print("Adding sample deliveries...")
    
    # Get or create staff user
    staff_user = User.objects.filter(is_staff=True).first()
    if not staff_user:
        staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
    
    # Sample deliveries data
    deliveries_data = [
        {
            'name': 'Alice Johnson',
            'email': 'alice.j@email.com',
            'phone': '+1-555-0201',
            'pickup': '123 Tech Street, San Jose, CA 95101',
            'delivery': '456 Innovation Drive, Palo Alto, CA 94301',
            'description': 'Smartphone and tablet package',
            'status': 'pending'
        },
        {
            'name': 'Bob Wilson',
            'email': 'bob.wilson@email.com',
            'phone': '+1-555-0202',
            'pickup': '789 Business Center, Dallas, TX 75201',
            'delivery': '321 Home Street, Fort Worth, TX 76101',
            'description': 'Office furniture and supplies',
            'status': 'confirmed'
        },
        {
            'name': 'Carol Davis',
            'email': 'carol.davis@email.com',
            'phone': '+1-555-0203',
            'pickup': '555 Shopping Mall, Atlanta, GA 30301',
            'delivery': '777 Residential Area, Savannah, GA 31401',
            'description': 'Home decor items and paintings',
            'status': 'in_transit'
        },
        {
            'name': 'David Miller',
            'email': 'david.miller@email.com',
            'phone': '+1-555-0204',
            'pickup': '888 Industrial Park, Boston, MA 02101',
            'delivery': '999 Suburban Lane, Worcester, MA 01601',
            'description': 'Industrial tools and equipment',
            'status': 'in_transit'
        },
        {
            'name': 'Eva Rodriguez',
            'email': 'eva.rodriguez@email.com',
            'phone': '+1-555-0205',
            'pickup': '222 Downtown Plaza, Philadelphia, PA 19101',
            'delivery': '444 University Drive, Pittsburgh, PA 15201',
            'description': 'Books and educational materials',
            'status': 'delivered'
        },
        {
            'name': 'Frank Thompson',
            'email': 'frank.thompson@email.com',
            'phone': '+1-555-0206',
            'pickup': '666 Warehouse District, Baltimore, MD 21201',
            'delivery': '111 Harbor View, Annapolis, MD 21401',
            'description': 'Marine equipment and supplies',
            'status': 'delivered'
        },
        {
            'name': 'Grace Lee',
            'email': 'grace.lee@email.com',
            'phone': '+1-555-0207',
            'pickup': '333 Tech Campus, Raleigh, NC 27601',
            'delivery': '555 Research Park, Durham, NC 27701',
            'description': 'Laboratory equipment and chemicals',
            'status': 'pending'
        },
        {
            'name': 'Henry Garcia',
            'email': 'henry.garcia@email.com',
            'phone': '+1-555-0208',
            'pickup': '777 Airport Road, Nashville, TN 37201',
            'delivery': '999 Music Row, Memphis, TN 38101',
            'description': 'Musical instruments and audio equipment',
            'status': 'confirmed'
        }
    ]
    
    status_descriptions = {
        'pending': 'Order received and pending confirmation',
        'confirmed': 'Order confirmed and being prepared for shipment',
        'in_transit': 'Package in transit to destination',
        'delivered': 'Package successfully delivered to recipient'
    }
    
    status_locations = {
        'pending': 'Origin Warehouse',
        'confirmed': 'Processing Center',
        'in_transit': 'Distribution Hub',
        'delivered': 'Customer Address'
    }
    
    for i, data in enumerate(deliveries_data):
        # Create delivery
        delivery = Delivery.objects.create(
            order_number=f"ORD-{2025:04d}-{1000+i:04d}",
            customer_name=data['name'],
            customer_email=data['email'],
            customer_phone=data['phone'],
            pickup_address=data['pickup'],
            delivery_address=data['delivery'],
            package_description=data['description'],
            package_weight=round(random.uniform(1.0, 25.0), 2),
            package_dimensions=f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)} cm",
            estimated_delivery=datetime.now() + timedelta(days=random.randint(1, 7)),
            current_status=data['status'],
            created_by=staff_user
        )
        
        # Create status update
        DeliveryStatus.objects.create(
            delivery=delivery,
            status=data['status'],
            location=status_locations[data['status']],
            description=status_descriptions[data['status']],
            created_at=datetime.now() - timedelta(days=random.randint(0, 3))
        )
        
        print(f"✅ Created: {data['name']} - {data['status']} - {delivery.tracking_number}")
    
    print(f"\n🎉 Added {len(deliveries_data)} new deliveries!")
    
    # Show summary
    total = Delivery.objects.count()
    pending = Delivery.objects.filter(current_status='pending').count()
    confirmed = Delivery.objects.filter(current_status='confirmed').count()
    in_transit = Delivery.objects.filter(current_status='in_transit').count()
    delivered = Delivery.objects.filter(current_status='delivered').count()
    
    print(f"\n📊 Current Database Summary:")
    print(f"   Total Deliveries: {total}")
    print(f"   Pending: {pending}")
    print(f"   Confirmed: {confirmed}")
    print(f"   In Transit: {in_transit}")
    print(f"   Delivered: {delivered}")

if __name__ == '__main__':
    add_sample_deliveries()
