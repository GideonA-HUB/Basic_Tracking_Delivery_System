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

def add_30_more_deliveries():
    print("Adding 30 more sample deliveries...")
    
    # Get or create staff user
    staff_user = User.objects.filter(is_staff=True).first()
    if not staff_user:
        staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
    
    # 30 more deliveries with diverse data
    deliveries_data = [
        {
            'name': 'Zoe Anderson',
            'email': 'zoe.anderson@email.com',
            'phone': '+1-555-0401',
            'pickup': '123 Pet Supply Warehouse, Portland, OR 97201',
            'delivery': '456 Veterinary Clinic, Eugene, OR 97401',
            'description': 'Veterinary equipment and pet care supplies',
            'status': 'pending',
            'order_number': 'ORD-2025-4001'
        },
        {
            'name': 'Nathan Lee',
            'email': 'nathan.lee@email.com',
            'phone': '+1-555-0402',
            'pickup': '789 Photography Studio, San Francisco, CA 94102',
            'delivery': '321 Art Gallery, Oakland, CA 94601',
            'description': 'Professional photography equipment and prints',
            'status': 'confirmed',
            'order_number': 'ORD-2025-4002'
        },
        {
            'name': 'Hannah White',
            'email': 'hannah.white@email.com',
            'phone': '+1-555-0403',
            'pickup': '555 Dance Academy, Miami, FL 33101',
            'delivery': '777 Performance Center, Orlando, FL 32801',
            'description': 'Dance costumes and performance equipment',
            'status': 'in_transit',
            'order_number': 'ORD-2025-4003'
        },
        {
            'name': 'Christopher Brown',
            'email': 'chris.brown@email.com',
            'phone': '+1-555-0404',
            'pickup': '888 Law Office, Washington, DC 20001',
            'delivery': '999 Courthouse, Alexandria, VA 22301',
            'description': 'Legal documents and court filing equipment',
            'status': 'delivered',
            'order_number': 'ORD-2025-4004'
        },
        {
            'name': 'Victoria Garcia',
            'email': 'victoria.garcia@email.com',
            'phone': '+1-555-0405',
            'pickup': '222 Beauty Salon Supply, Los Angeles, CA 90001',
            'delivery': '444 Spa Resort, Palm Springs, CA 92262',
            'description': 'Beauty and spa equipment supplies',
            'status': 'pending',
            'order_number': 'ORD-2025-4005'
        },
        {
            'name': 'Andrew Miller',
            'email': 'andrew.miller@email.com',
            'phone': '+1-555-0406',
            'pickup': '666 Fitness Equipment Warehouse, Las Vegas, NV 89101',
            'delivery': '888 Gym Facility, Henderson, NV 89002',
            'description': 'Commercial fitness equipment and accessories',
            'status': 'confirmed',
            'order_number': 'ORD-2025-4006'
        },
        {
            'name': 'Samantha Taylor',
            'email': 'samantha.taylor@email.com',
            'phone': '+1-555-0407',
            'pickup': '111 Book Publishing House, New York, NY 10001',
            'delivery': '333 Library Distribution Center, Newark, NJ 07101',
            'description': 'Books and publishing materials',
            'status': 'in_transit',
            'order_number': 'ORD-2025-4007'
        },
        {
            'name': 'Kevin Johnson',
            'email': 'kevin.johnson@email.com',
            'phone': '+1-555-0408',
            'pickup': '444 Music Instrument Factory, Nashville, TN 37201',
            'delivery': '666 Music Store, Memphis, TN 38101',
            'description': 'Musical instruments and sound equipment',
            'status': 'delivered',
            'order_number': 'ORD-2025-4008'
        },
        {
            'name': 'Rachel Davis',
            'email': 'rachel.davis@email.com',
            'phone': '+1-555-0409',
            'pickup': '777 Fashion Design Studio, Atlanta, GA 30301',
            'delivery': '999 Boutique Store, Savannah, GA 31401',
            'description': 'Designer clothing and fashion accessories',
            'status': 'pending',
            'order_number': 'ORD-2025-4009'
        },
        {
            'name': 'Jonathan Wilson',
            'email': 'jonathan.wilson@email.com',
            'phone': '+1-555-0410',
            'pickup': '888 Tech Startup Incubator, Austin, TX 73301',
            'delivery': '111 Innovation Center, San Antonio, TX 78201',
            'description': 'Startup equipment and office supplies',
            'status': 'confirmed',
            'order_number': 'ORD-2025-4010'
        },
        {
            'name': 'Amanda Rodriguez',
            'email': 'amanda.rodriguez@email.com',
            'phone': '+1-555-0411',
            'pickup': '222 Dental Equipment Supplier, Phoenix, AZ 85001',
            'delivery': '444 Dental Clinic, Tucson, AZ 85701',
            'description': 'Dental equipment and medical supplies',
            'status': 'in_transit',
            'order_number': 'ORD-2025-4011'
        },
        {
            'name': 'Brandon Martinez',
            'email': 'brandon.martinez@email.com',
            'phone': '+1-555-0412',
            'pickup': '555 Construction Material Yard, Denver, CO 80201',
            'delivery': '777 Building Site, Boulder, CO 80301',
            'description': 'Construction materials and tools',
            'status': 'delivered',
            'order_number': 'ORD-2025-4012'
        },
        {
            'name': 'Nicole Thompson',
            'email': 'nicole.thompson@email.com',
            'phone': '+1-555-0413',
            'pickup': '888 Jewelry Manufacturing Plant, Providence, RI 02901',
            'delivery': '999 Jewelry Store, Newport, RI 02840',
            'description': 'Precious jewelry and gemstones',
            'status': 'pending',
            'order_number': 'ORD-2025-4013'
        },
        {
            'name': 'Steven Anderson',
            'email': 'steven.anderson@email.com',
            'phone': '+1-555-0414',
            'pickup': '111 Automotive Parts Factory, Detroit, MI 48201',
            'delivery': '333 Car Dealership, Ann Arbor, MI 48103',
            'description': 'Automotive parts and accessories',
            'status': 'confirmed',
            'order_number': 'ORD-2025-4014'
        },
        {
            'name': 'Melissa Chen',
            'email': 'melissa.chen@email.com',
            'phone': '+1-555-0415',
            'pickup': '444 Pharmaceutical Research Lab, Boston, MA 02101',
            'delivery': '666 Medical Center, Cambridge, MA 02139',
            'description': 'Pharmaceutical research equipment',
            'status': 'in_transit',
            'order_number': 'ORD-2025-4015'
        },
        {
            'name': 'Robert Kim',
            'email': 'robert.kim@email.com',
            'phone': '+1-555-0416',
            'pickup': '777 Electronics Manufacturing Plant, San Jose, CA 95101',
            'delivery': '999 Tech Store, Mountain View, CA 94043',
            'description': 'Consumer electronics and gadgets',
            'status': 'delivered',
            'order_number': 'ORD-2025-4016'
        },
        {
            'name': 'Jennifer Lee',
            'email': 'jennifer.lee@email.com',
            'phone': '+1-555-0417',
            'pickup': '888 Textile Factory, Charlotte, NC 28201',
            'delivery': '111 Clothing Store, Raleigh, NC 27601',
            'description': 'Textiles and fabric materials',
            'status': 'pending',
            'order_number': 'ORD-2025-4017'
        },
        {
            'name': 'Michael White',
            'email': 'michael.white@email.com',
            'phone': '+1-555-0418',
            'pickup': '222 Furniture Manufacturing Plant, Grand Rapids, MI 49501',
            'delivery': '444 Furniture Store, Lansing, MI 48901',
            'description': 'Custom furniture and home decor',
            'status': 'confirmed',
            'order_number': 'ORD-2025-4018'
        },
        {
            'name': 'Sarah Johnson',
            'email': 'sarah.johnson@email.com',
            'phone': '+1-555-0419',
            'pickup': '555 Toy Manufacturing Factory, Pawtucket, RI 02860',
            'delivery': '777 Toy Store, Providence, RI 02901',
            'description': 'Children toys and educational materials',
            'status': 'in_transit',
            'order_number': 'ORD-2025-4019'
        },
        {
            'name': 'David Brown',
            'email': 'david.brown@email.com',
            'phone': '+1-555-0420',
            'pickup': '888 Sporting Goods Factory, Springfield, MA 01101',
            'delivery': '999 Sports Store, Worcester, MA 01601',
            'description': 'Sports equipment and athletic gear',
            'status': 'delivered',
            'order_number': 'ORD-2025-4020'
        },
        {
            'name': 'Lisa Garcia',
            'email': 'lisa.garcia@email.com',
            'phone': '+1-555-0421',
            'pickup': '111 Cosmetics Manufacturing Plant, Los Angeles, CA 90001',
            'delivery': '333 Beauty Store, Beverly Hills, CA 90210',
            'description': 'Cosmetics and beauty products',
            'status': 'pending',
            'order_number': 'ORD-2025-4021'
        },
        {
            'name': 'Thomas Martinez',
            'email': 'thomas.martinez@email.com',
            'phone': '+1-555-0422',
            'pickup': '444 Wine Production Facility, Napa Valley, CA 94558',
            'delivery': '666 Wine Store, San Francisco, CA 94102',
            'description': 'Premium wines and spirits',
            'status': 'confirmed',
            'order_number': 'ORD-2025-4022'
        },
        {
            'name': 'Michelle Rodriguez',
            'email': 'michelle.rodriguez@email.com',
            'phone': '+1-555-0423',
            'pickup': '777 Coffee Roasting Plant, Seattle, WA 98101',
            'delivery': '999 Coffee Shop, Bellevue, WA 98004',
            'description': 'Premium coffee beans and equipment',
            'status': 'in_transit',
            'order_number': 'ORD-2025-4023'
        },
        {
            'name': 'Daniel Thompson',
            'email': 'daniel.thompson@email.com',
            'phone': '+1-555-0424',
            'pickup': '888 Chocolate Factory, Hershey, PA 17033',
            'delivery': '111 Candy Store, Philadelphia, PA 19101',
            'description': 'Chocolate and confectionery products',
            'status': 'delivered',
            'order_number': 'ORD-2025-4024'
        },
        {
            'name': 'Jessica Anderson',
            'email': 'jessica.anderson@email.com',
            'phone': '+1-555-0425',
            'pickup': '222 Perfume Manufacturing Plant, Grasse, France',
            'delivery': '444 Perfume Store, New York, NY 10001',
            'description': 'Luxury perfumes and fragrances',
            'status': 'pending',
            'order_number': 'ORD-2025-4025'
        },
        {
            'name': 'Ryan Wilson',
            'email': 'ryan.wilson@email.com',
            'phone': '+1-555-0426',
            'pickup': '555 Watch Manufacturing Plant, Geneva, Switzerland',
            'delivery': '777 Watch Store, Miami, FL 33101',
            'description': 'Luxury watches and timepieces',
            'status': 'confirmed',
            'order_number': 'ORD-2025-4026'
        },
        {
            'name': 'Ashley Davis',
            'email': 'ashley.davis@email.com',
            'phone': '+1-555-0427',
            'pickup': '888 Diamond Cutting Facility, Antwerp, Belgium',
            'delivery': '999 Jewelry Store, Los Angeles, CA 90001',
            'description': 'Diamonds and precious stones',
            'status': 'in_transit',
            'order_number': 'ORD-2025-4027'
        },
        {
            'name': 'Matthew Johnson',
            'email': 'matthew.johnson@email.com',
            'phone': '+1-555-0428',
            'pickup': '111 Leather Goods Factory, Florence, Italy',
            'delivery': '333 Leather Store, Chicago, IL 60601',
            'description': 'Luxury leather goods and accessories',
            'status': 'delivered',
            'order_number': 'ORD-2025-4028'
        },
        {
            'name': 'Emily Brown',
            'email': 'emily.brown@email.com',
            'phone': '+1-555-0429',
            'pickup': '444 Silk Production Facility, Lyon, France',
            'delivery': '666 Fashion Store, New York, NY 10001',
            'description': 'Luxury silk fabrics and materials',
            'status': 'pending',
            'order_number': 'ORD-2025-4029'
        },
        {
            'name': 'Christopher Lee',
            'email': 'christopher.lee@email.com',
            'phone': '+1-555-0430',
            'pickup': '777 Crystal Manufacturing Plant, Murano, Italy',
            'delivery': '999 Crystal Store, Las Vegas, NV 89101',
            'description': 'Artisan crystal and glassware',
            'status': 'confirmed',
            'order_number': 'ORD-2025-4030'
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
            package_weight=round(random.uniform(0.5, 75.0), 2),
            package_dimensions=f"{random.randint(5, 150)}x{random.randint(5, 150)}x{random.randint(3, 80)} cm",
            estimated_delivery=timezone.now() + timedelta(days=random.randint(1, 21)),
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
    print(f"   - Veterinary & Pet Care Equipment")
    print(f"   - Photography & Art Supplies")
    print(f"   - Dance & Performance Gear")
    print(f"   - Legal & Court Documents")
    print(f"   - Beauty & Spa Equipment")
    print(f"   - Fitness & Sports Equipment")
    print(f"   - Books & Publishing Materials")
    print(f"   - Musical Instruments")
    print(f"   - Fashion & Textiles")
    print(f"   - Tech Startup Equipment")
    print(f"   - Medical & Dental Supplies")
    print(f"   - Construction Materials")
    print(f"   - Jewelry & Precious Stones")
    print(f"   - Automotive Parts")
    print(f"   - Electronics & Gadgets")
    print(f"   - Furniture & Home Decor")
    print(f"   - Toys & Educational Materials")
    print(f"   - Cosmetics & Beauty Products")
    print(f"   - Wine & Spirits")
    print(f"   - Coffee & Beverages")
    print(f"   - Chocolate & Confectionery")
    print(f"   - Luxury Perfumes")
    print(f"   - Luxury Watches")
    print(f"   - Diamonds & Precious Stones")
    print(f"   - Leather Goods")
    print(f"   - Silk Fabrics")
    print(f"   - Artisan Crystal")
    print(f"   - And many more diverse packages!")

if __name__ == '__main__':
    add_30_more_deliveries()
