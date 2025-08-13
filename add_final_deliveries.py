#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import random
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from tracking.models import Delivery, DeliveryStatus
from django.contrib.auth.models import User

def add_final_deliveries():
    print("Adding final sample deliveries...")
    
    # Get or create staff user
    staff_user = User.objects.filter(is_staff=True).first()
    if not staff_user:
        staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
    
    # Final deliveries data
    deliveries_data = [
        {
            'name': 'Grace Lee',
            'email': 'grace.lee@email.com',
            'phone': '+1-555-0207',
            'pickup': '333 Tech Campus, Raleigh, NC 27601',
            'delivery': '555 Research Park, Durham, NC 27701',
            'description': 'Laboratory equipment and chemicals',
            'status': 'pending',
            'order_number': 'ORD-2025-2007'
        },
        {
            'name': 'Henry Garcia',
            'email': 'henry.garcia@email.com',
            'phone': '+1-555-0208',
            'pickup': '777 Airport Road, Nashville, TN 37201',
            'delivery': '999 Music Row, Memphis, TN 38101',
            'description': 'Musical instruments and audio equipment',
            'status': 'confirmed',
            'order_number': 'ORD-2025-2008'
        },
        {
            'name': 'Isabella Chen',
            'email': 'isabella.chen@email.com',
            'phone': '+1-555-0209',
            'pickup': '444 Innovation Hub, Austin, TX 73301',
            'delivery': '666 Startup Street, San Antonio, TX 78201',
            'description': 'Software and hardware development kits',
            'status': 'in_transit',
            'order_number': 'ORD-2025-2009'
        },
        {
            'name': 'James Anderson',
            'email': 'james.anderson@email.com',
            'phone': '+1-555-0210',
            'pickup': '888 Creative District, Portland, OR 97201',
            'delivery': '111 Artisan Way, Eugene, OR 97401',
            'description': 'Art supplies and creative materials',
            'status': 'delivered',
            'order_number': 'ORD-2025-2010'
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
    
    created_count = 0
    
    for data in deliveries_data:
        # Check if order number already exists
        if Delivery.objects.filter(order_number=data['order_number']).exists():
            print(f"⚠️  Skipping {data['name']} - Order number {data['order_number']} already exists")
            continue
            
        # Create delivery with timezone-aware datetime
        delivery = Delivery.objects.create(
            order_number=data['order_number'],
            customer_name=data['name'],
            customer_email=data['email'],
            customer_phone=data['phone'],
            pickup_address=data['pickup'],
            delivery_address=data['delivery'],
            package_description=data['description'],
            package_weight=round(random.uniform(1.0, 25.0), 2),
            package_dimensions=f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)} cm",
            estimated_delivery=timezone.now() + timedelta(days=random.randint(1, 7)),
            current_status=data['status'],
            created_by=staff_user
        )
        
        # Create status update
        DeliveryStatus.objects.create(
            delivery=delivery,
            status=data['status'],
            location=status_locations[data['status']],
            description=status_descriptions[data['status']]
        )
        
        print(f"✅ Created: {data['name']} - {data['status']} - {delivery.tracking_number}")
        created_count += 1
    
    print(f"\n🎉 Added {created_count} new deliveries!")
    
    # Show final summary
    total = Delivery.objects.count()
    pending = Delivery.objects.filter(current_status='pending').count()
    confirmed = Delivery.objects.filter(current_status='confirmed').count()
    in_transit = Delivery.objects.filter(current_status='in_transit').count()
    delivered = Delivery.objects.filter(current_status='delivered').count()
    
    print(f"\n📊 Final Database Summary:")
    print(f"   Total Deliveries: {total}")
    print(f"   Pending: {pending}")
    print(f"   Confirmed: {confirmed}")
    print(f"   In Transit: {in_transit}")
    print(f"   Delivered: {delivered}")
    
    print(f"\n🎯 Status Distribution:")
    print(f"   Pending: {pending}/{total} ({pending/total*100:.1f}%)")
    print(f"   Confirmed: {confirmed}/{total} ({confirmed/total*100:.1f}%)")
    print(f"   In Transit: {in_transit}/{total} ({in_transit/total*100:.1f}%)")
    print(f"   Delivered: {delivered}/{total} ({delivered/total*100:.1f}%)")

if __name__ == '__main__':
    add_final_deliveries()
