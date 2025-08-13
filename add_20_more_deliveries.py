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

def add_20_more_deliveries():
    print("Adding 20 more sample deliveries...")
    
    # Get or create staff user
    staff_user = User.objects.filter(is_staff=True).first()
    if not staff_user:
        staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
    
    # 20 more deliveries with diverse data
    deliveries_data = [
        {
            'name': 'Maria Rodriguez',
            'email': 'maria.rodriguez@email.com',
            'phone': '+1-555-0301',
            'pickup': '123 Fashion District, Los Angeles, CA 90015',
            'delivery': '456 Designer Blvd, Beverly Hills, CA 90210',
            'description': 'Luxury clothing and accessories collection',
            'status': 'pending',
            'order_number': 'ORD-2025-3001'
        },
        {
            'name': 'Alex Thompson',
            'email': 'alex.thompson@email.com',
            'phone': '+1-555-0302',
            'pickup': '789 Tech Innovation Center, Seattle, WA 98101',
            'delivery': '321 Startup Alley, Bellevue, WA 98004',
            'description': 'Advanced robotics and AI equipment',
            'status': 'confirmed',
            'order_number': 'ORD-2025-3002'
        },
        {
            'name': 'Sophie Chen',
            'email': 'sophie.chen@email.com',
            'phone': '+1-555-0303',
            'pickup': '555 Medical Research Park, Boston, MA 02114',
            'delivery': '777 Healthcare Campus, Cambridge, MA 02139',
            'description': 'Medical research equipment and supplies',
            'status': 'in_transit',
            'order_number': 'ORD-2025-3003'
        },
        {
            'name': 'Marcus Johnson',
            'email': 'marcus.johnson@email.com',
            'phone': '+1-555-0304',
            'pickup': '888 Sports Complex, Miami, FL 33132',
            'delivery': '999 Athletic Center, Fort Lauderdale, FL 33301',
            'description': 'Professional sports equipment and gear',
            'status': 'delivered',
            'order_number': 'ORD-2025-3004'
        },
        {
            'name': 'Emma Wilson',
            'email': 'emma.wilson@email.com',
            'phone': '+1-555-0305',
            'pickup': '222 Art Gallery District, New York, NY 10001',
            'delivery': '444 Creative Studio, Brooklyn, NY 11201',
            'description': 'Fine art pieces and gallery equipment',
            'status': 'pending',
            'order_number': 'ORD-2025-3005'
        },
        {
            'name': 'Daniel Kim',
            'email': 'daniel.kim@email.com',
            'phone': '+1-555-0306',
            'pickup': '666 Electronics Hub, San Jose, CA 95113',
            'delivery': '888 Innovation Lab, Mountain View, CA 94043',
            'description': 'Cutting-edge electronics and prototypes',
            'status': 'confirmed',
            'order_number': 'ORD-2025-3006'
        },
        {
            'name': 'Olivia Davis',
            'email': 'olivia.davis@email.com',
            'phone': '+1-555-0307',
            'pickup': '111 Music Production Studio, Nashville, TN 37201',
            'delivery': '333 Recording Studio, Franklin, TN 37064',
            'description': 'Professional audio equipment and instruments',
            'status': 'in_transit',
            'order_number': 'ORD-2025-3007'
        },
        {
            'name': 'Ryan Martinez',
            'email': 'ryan.martinez@email.com',
            'phone': '+1-555-0308',
            'pickup': '444 Aerospace Facility, Houston, TX 77001',
            'delivery': '666 Space Center, Clear Lake, TX 77058',
            'description': 'Aerospace components and satellite parts',
            'status': 'delivered',
            'order_number': 'ORD-2025-3008'
        },
        {
            'name': 'Isabella Brown',
            'email': 'isabella.brown@email.com',
            'phone': '+1-555-0309',
            'pickup': '777 Culinary Institute, New Orleans, LA 70112',
            'delivery': '999 Restaurant District, Baton Rouge, LA 70801',
            'description': 'Professional kitchen equipment and supplies',
            'status': 'pending',
            'order_number': 'ORD-2025-3009'
        },
        {
            'name': 'Lucas Anderson',
            'email': 'lucas.anderson@email.com',
            'phone': '+1-555-0310',
            'pickup': '888 Gaming Development Studio, Austin, TX 73301',
            'delivery': '111 Entertainment Complex, San Antonio, TX 78201',
            'description': 'Gaming hardware and development equipment',
            'status': 'confirmed',
            'order_number': 'ORD-2025-3010'
        },
        {
            'name': 'Ava Garcia',
            'email': 'ava.garcia@email.com',
            'phone': '+1-555-0311',
            'pickup': '222 Fashion Design Studio, Atlanta, GA 30301',
            'delivery': '444 Boutique District, Savannah, GA 31401',
            'description': 'Designer clothing and fashion accessories',
            'status': 'in_transit',
            'order_number': 'ORD-2025-3011'
        },
        {
            'name': 'Noah Taylor',
            'email': 'noah.taylor@email.com',
            'phone': '+1-555-0312',
            'pickup': '555 Renewable Energy Plant, Denver, CO 80201',
            'delivery': '777 Green Technology Center, Boulder, CO 80301',
            'description': 'Solar panels and renewable energy equipment',
            'status': 'delivered',
            'order_number': 'ORD-2025-3012'
        },
        {
            'name': 'Mia Rodriguez',
            'email': 'mia.rodriguez@email.com',
            'phone': '+1-555-0313',
            'pickup': '888 Film Production Studio, Los Angeles, CA 90028',
            'delivery': '999 Entertainment District, Hollywood, CA 90027',
            'description': 'Film equipment and production gear',
            'status': 'pending',
            'order_number': 'ORD-2025-3013'
        },
        {
            'name': 'Ethan Wilson',
            'email': 'ethan.wilson@email.com',
            'phone': '+1-555-0314',
            'pickup': '111 Biotechnology Lab, San Diego, CA 92101',
            'delivery': '333 Research Campus, La Jolla, CA 92037',
            'description': 'Biotech equipment and laboratory supplies',
            'status': 'confirmed',
            'order_number': 'ORD-2025-3014'
        },
        {
            'name': 'Chloe Thompson',
            'email': 'chloe.thompson@email.com',
            'phone': '+1-555-0315',
            'pickup': '444 Jewelry Design Studio, New York, NY 10001',
            'delivery': '666 Luxury Retail District, Manhattan, NY 10022',
            'description': 'Precious metals and jewelry making equipment',
            'status': 'in_transit',
            'order_number': 'ORD-2025-3015'
        },
        {
            'name': 'William Chen',
            'email': 'william.chen@email.com',
            'phone': '+1-555-0316',
            'pickup': '777 Automotive Manufacturing Plant, Detroit, MI 48201',
            'delivery': '999 Car Dealership District, Ann Arbor, MI 48103',
            'description': 'Automotive parts and manufacturing equipment',
            'status': 'delivered',
            'order_number': 'ORD-2025-3016'
        },
        {
            'name': 'Sofia Johnson',
            'email': 'sofia.johnson@email.com',
            'phone': '+1-555-0317',
            'pickup': '888 Pharmaceutical Research Center, Philadelphia, PA 19101',
            'delivery': '999 Medical Campus, Pittsburgh, PA 15201',
            'description': 'Pharmaceutical research equipment and chemicals',
            'status': 'pending',
            'order_number': 'ORD-2025-3017'
        },
        {
            'name': 'James Davis',
            'email': 'james.davis@email.com',
            'phone': '+1-555-0318',
            'pickup': '111 Construction Equipment Yard, Chicago, IL 60601',
            'delivery': '333 Building Site, Evanston, IL 60201',
            'description': 'Heavy construction machinery and tools',
            'status': 'confirmed',
            'order_number': 'ORD-2025-3018'
        },
        {
            'name': 'Charlotte Brown',
            'email': 'charlotte.brown@email.com',
            'phone': '+1-555-0319',
            'pickup': '444 Interior Design Studio, Dallas, TX 75201',
            'delivery': '666 Home Decor District, Fort Worth, TX 76101',
            'description': 'Interior design furniture and decorative items',
            'status': 'in_transit',
            'order_number': 'ORD-2025-3019'
        },
        {
            'name': 'Benjamin Martinez',
            'email': 'benjamin.martinez@email.com',
            'phone': '+1-555-0320',
            'pickup': '777 Marine Research Institute, San Francisco, CA 94101',
            'delivery': '999 Ocean Science Center, Monterey, CA 93940',
            'description': 'Marine research equipment and oceanographic tools',
            'status': 'delivered',
            'order_number': 'ORD-2025-3020'
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
            package_weight=round(random.uniform(1.0, 50.0), 2),
            package_dimensions=f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)} cm",
            estimated_delivery=timezone.now() + timedelta(days=random.randint(1, 14)),
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
    
    # Show comprehensive summary
    total = Delivery.objects.count()
    pending = Delivery.objects.filter(current_status='pending').count()
    confirmed = Delivery.objects.filter(current_status='confirmed').count()
    in_transit = Delivery.objects.filter(current_status='in_transit').count()
    delivered = Delivery.objects.filter(current_status='delivered').count()
    
    print(f"\n📊 Complete Database Summary:")
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
    
    print(f"\n🌟 New Deliveries Added:")
    print(f"   - Luxury Fashion Items")
    print(f"   - Technology & Electronics")
    print(f"   - Medical & Research Equipment")
    print(f"   - Sports & Entertainment Gear")
    print(f"   - Art & Creative Supplies")
    print(f"   - Professional Equipment")
    print(f"   - And many more diverse packages!")

if __name__ == '__main__':
    add_20_more_deliveries()
