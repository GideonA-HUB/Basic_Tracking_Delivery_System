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

def add_37_more_deliveries():
    print("Adding 37 more sample deliveries...")
    
    # Get or create staff user
    staff_user = User.objects.filter(is_staff=True).first()
    if not staff_user:
        staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
    
    # 37 more deliveries with diverse data
    deliveries_data = [
        {
            'name': 'Isabella Rodriguez',
            'email': 'isabella.rodriguez@email.com',
            'phone': '+1-555-0501',
            'pickup': '123 Organic Farm, Fresno, CA 93701',
            'delivery': '456 Farmers Market, Sacramento, CA 95814',
            'description': 'Fresh organic produce and farm products',
            'status': 'pending',
            'order_number': 'ORD-2025-5001'
        },
        {
            'name': 'Alexander Thompson',
            'email': 'alexander.thompson@email.com',
            'phone': '+1-555-0502',
            'pickup': '789 Solar Panel Factory, Albuquerque, NM 87101',
            'delivery': '321 Green Energy Center, Santa Fe, NM 87501',
            'description': 'Solar panels and renewable energy systems',
            'status': 'confirmed',
            'order_number': 'ORD-2025-5002'
        },
        {
            'name': 'Sophia Chen',
            'email': 'sophia.chen@email.com',
            'phone': '+1-555-0503',
            'pickup': '555 Biotechnology Research Lab, San Diego, CA 92101',
            'delivery': '777 Medical Innovation Center, La Jolla, CA 92037',
            'description': 'Biotech research equipment and samples',
            'status': 'in_transit',
            'order_number': 'ORD-2025-5003'
        },
        {
            'name': 'William Johnson',
            'email': 'william.johnson@email.com',
            'phone': '+1-555-0504',
            'pickup': '888 Aerospace Manufacturing Plant, Wichita, KS 67201',
            'delivery': '999 Aviation Center, Kansas City, MO 64101',
            'description': 'Aircraft parts and aviation equipment',
            'status': 'delivered',
            'order_number': 'ORD-2025-5004'
        },
        {
            'name': 'Olivia Davis',
            'email': 'olivia.davis@email.com',
            'phone': '+1-555-0505',
            'pickup': '222 Fashion Design Studio, Los Angeles, CA 90001',
            'delivery': '444 Luxury Boutique, Beverly Hills, CA 90210',
            'description': 'Designer clothing and accessories',
            'status': 'pending',
            'order_number': 'ORD-2025-5005'
        },
        {
            'name': 'James Wilson',
            'email': 'james.wilson@email.com',
            'phone': '+1-555-0506',
            'pickup': '666 Tech Startup Incubator, Austin, TX 73301',
            'delivery': '888 Innovation Hub, Dallas, TX 75201',
            'description': 'Startup equipment and technology supplies',
            'status': 'confirmed',
            'order_number': 'ORD-2025-5006'
        },
        {
            'name': 'Ava Brown',
            'email': 'ava.brown@email.com',
            'phone': '+1-555-0507',
            'pickup': '111 Art Gallery Warehouse, New York, NY 10001',
            'delivery': '333 Contemporary Art Museum, Brooklyn, NY 11201',
            'description': 'Fine art pieces and gallery equipment',
            'status': 'in_transit',
            'order_number': 'ORD-2025-5007'
        },
        {
            'name': 'Benjamin Garcia',
            'email': 'benjamin.garcia@email.com',
            'phone': '+1-555-0508',
            'pickup': '444 Music Production Studio, Nashville, TN 37201',
            'delivery': '666 Recording Studio, Memphis, TN 38101',
            'description': 'Professional audio equipment and instruments',
            'status': 'delivered',
            'order_number': 'ORD-2025-5008'
        },
        {
            'name': 'Mia Martinez',
            'email': 'mia.martinez@email.com',
            'phone': '+1-555-0509',
            'pickup': '777 Jewelry Manufacturing Plant, Providence, RI 02901',
            'delivery': '999 Luxury Jewelry Store, Newport, RI 02840',
            'description': 'Precious jewelry and gemstones',
            'status': 'pending',
            'order_number': 'ORD-2025-5009'
        },
        {
            'name': 'Ethan Anderson',
            'email': 'ethan.anderson@email.com',
            'phone': '+1-555-0510',
            'pickup': '888 Automotive Parts Factory, Detroit, MI 48201',
            'delivery': '111 Car Dealership, Ann Arbor, MI 48103',
            'description': 'Automotive parts and accessories',
            'status': 'confirmed',
            'order_number': 'ORD-2025-5010'
        },
        {
            'name': 'Charlotte Taylor',
            'email': 'charlotte.taylor@email.com',
            'phone': '+1-555-0511',
            'pickup': '222 Pharmaceutical Research Lab, Boston, MA 02101',
            'delivery': '444 Medical Center, Cambridge, MA 02139',
            'description': 'Pharmaceutical research equipment',
            'status': 'in_transit',
            'order_number': 'ORD-2025-5011'
        },
        {
            'name': 'Lucas Lee',
            'email': 'lucas.lee@email.com',
            'phone': '+1-555-0512',
            'pickup': '555 Electronics Manufacturing Plant, San Jose, CA 95101',
            'delivery': '777 Tech Store, Mountain View, CA 94043',
            'description': 'Consumer electronics and gadgets',
            'status': 'delivered',
            'order_number': 'ORD-2025-5012'
        },
        {
            'name': 'Amelia White',
            'email': 'amelia.white@email.com',
            'phone': '+1-555-0513',
            'pickup': '888 Textile Factory, Charlotte, NC 28201',
            'delivery': '111 Clothing Store, Raleigh, NC 27601',
            'description': 'Textiles and fabric materials',
            'status': 'pending',
            'order_number': 'ORD-2025-5013'
        },
        {
            'name': 'Mason Johnson',
            'email': 'mason.johnson@email.com',
            'phone': '+1-555-0514',
            'pickup': '222 Furniture Manufacturing Plant, Grand Rapids, MI 49501',
            'delivery': '444 Furniture Store, Lansing, MI 48901',
            'description': 'Custom furniture and home decor',
            'status': 'confirmed',
            'order_number': 'ORD-2025-5014'
        },
        {
            'name': 'Harper Davis',
            'email': 'harper.davis@email.com',
            'phone': '+1-555-0515',
            'pickup': '555 Toy Manufacturing Factory, Pawtucket, RI 02860',
            'delivery': '777 Toy Store, Providence, RI 02901',
            'description': 'Children toys and educational materials',
            'status': 'in_transit',
            'order_number': 'ORD-2025-5015'
        },
        {
            'name': 'Evelyn Brown',
            'email': 'evelyn.brown@email.com',
            'phone': '+1-555-0516',
            'pickup': '888 Sporting Goods Factory, Springfield, MA 01101',
            'delivery': '999 Sports Store, Worcester, MA 01601',
            'description': 'Sports equipment and athletic gear',
            'status': 'delivered',
            'order_number': 'ORD-2025-5016'
        },
        {
            'name': 'Logan Garcia',
            'email': 'logan.garcia@email.com',
            'phone': '+1-555-0517',
            'pickup': '111 Cosmetics Manufacturing Plant, Los Angeles, CA 90001',
            'delivery': '333 Beauty Store, Beverly Hills, CA 90210',
            'description': 'Cosmetics and beauty products',
            'status': 'pending',
            'order_number': 'ORD-2025-5017'
        },
        {
            'name': 'Abigail Martinez',
            'email': 'abigail.martinez@email.com',
            'phone': '+1-555-0518',
            'pickup': '444 Wine Production Facility, Napa Valley, CA 94558',
            'delivery': '666 Wine Store, San Francisco, CA 94102',
            'description': 'Premium wines and spirits',
            'status': 'confirmed',
            'order_number': 'ORD-2025-5018'
        },
        {
            'name': 'Sebastian Anderson',
            'email': 'sebastian.anderson@email.com',
            'phone': '+1-555-0519',
            'pickup': '777 Coffee Roasting Plant, Seattle, WA 98101',
            'delivery': '999 Coffee Shop, Bellevue, WA 98004',
            'description': 'Premium coffee beans and equipment',
            'status': 'in_transit',
            'order_number': 'ORD-2025-5019'
        },
        {
            'name': 'Elizabeth Taylor',
            'email': 'elizabeth.taylor@email.com',
            'phone': '+1-555-0520',
            'pickup': '888 Chocolate Factory, Hershey, PA 17033',
            'delivery': '111 Candy Store, Philadelphia, PA 19101',
            'description': 'Chocolate and confectionery products',
            'status': 'delivered',
            'order_number': 'ORD-2025-5020'
        },
        {
            'name': 'Jackson Lee',
            'email': 'jackson.lee@email.com',
            'phone': '+1-555-0521',
            'pickup': '222 Perfume Manufacturing Plant, Grasse, France',
            'delivery': '444 Perfume Store, New York, NY 10001',
            'description': 'Luxury perfumes and fragrances',
            'status': 'pending',
            'order_number': 'ORD-2025-5021'
        },
        {
            'name': 'Sofia White',
            'email': 'sofia.white@email.com',
            'phone': '+1-555-0522',
            'pickup': '555 Watch Manufacturing Plant, Geneva, Switzerland',
            'delivery': '777 Watch Store, Miami, FL 33101',
            'description': 'Luxury watches and timepieces',
            'status': 'confirmed',
            'order_number': 'ORD-2025-5022'
        },
        {
            'name': 'Aiden Johnson',
            'email': 'aiden.johnson@email.com',
            'phone': '+1-555-0523',
            'pickup': '888 Diamond Cutting Facility, Antwerp, Belgium',
            'delivery': '999 Jewelry Store, Los Angeles, CA 90001',
            'description': 'Diamonds and precious stones',
            'status': 'in_transit',
            'order_number': 'ORD-2025-5023'
        },
        {
            'name': 'Madison Davis',
            'email': 'madison.davis@email.com',
            'phone': '+1-555-0524',
            'pickup': '111 Leather Goods Factory, Florence, Italy',
            'delivery': '333 Leather Store, Chicago, IL 60601',
            'description': 'Luxury leather goods and accessories',
            'status': 'delivered',
            'order_number': 'ORD-2025-5024'
        },
        {
            'name': 'Grayson Brown',
            'email': 'grayson.brown@email.com',
            'phone': '+1-555-0525',
            'pickup': '444 Silk Production Facility, Lyon, France',
            'delivery': '666 Fashion Store, New York, NY 10001',
            'description': 'Luxury silk fabrics and materials',
            'status': 'pending',
            'order_number': 'ORD-2025-5025'
        },
        {
            'name': 'Layla Garcia',
            'email': 'layla.garcia@email.com',
            'phone': '+1-555-0526',
            'pickup': '777 Crystal Manufacturing Plant, Murano, Italy',
            'delivery': '999 Crystal Store, Las Vegas, NV 89101',
            'description': 'Artisan crystal and glassware',
            'status': 'confirmed',
            'order_number': 'ORD-2025-5026'
        },
        {
            'name': 'Carter Martinez',
            'email': 'carter.martinez@email.com',
            'phone': '+1-555-0527',
            'pickup': '888 Marine Research Institute, San Francisco, CA 94101',
            'delivery': '999 Ocean Science Center, Monterey, CA 93940',
            'description': 'Marine research equipment and oceanographic tools',
            'status': 'in_transit',
            'order_number': 'ORD-2025-5027'
        },
        {
            'name': 'Scarlett Anderson',
            'email': 'scarlett.anderson@email.com',
            'phone': '+1-555-0528',
            'pickup': '111 Pet Supply Warehouse, Portland, OR 97201',
            'delivery': '333 Veterinary Clinic, Eugene, OR 97401',
            'description': 'Veterinary equipment and pet care supplies',
            'status': 'delivered',
            'order_number': 'ORD-2025-5028'
        },
        {
            'name': 'Jayden Taylor',
            'email': 'jayden.taylor@email.com',
            'phone': '+1-555-0529',
            'pickup': '444 Photography Studio, San Francisco, CA 94102',
            'delivery': '666 Art Gallery, Oakland, CA 94601',
            'description': 'Professional photography equipment and prints',
            'status': 'pending',
            'order_number': 'ORD-2025-5029'
        },
        {
            'name': 'Luna Lee',
            'email': 'luna.lee@email.com',
            'phone': '+1-555-0530',
            'pickup': '777 Dance Academy, Miami, FL 33101',
            'delivery': '999 Performance Center, Orlando, FL 32801',
            'description': 'Dance costumes and performance equipment',
            'status': 'confirmed',
            'order_number': 'ORD-2025-5030'
        },
        {
            'name': 'Hunter White',
            'email': 'hunter.white@email.com',
            'phone': '+1-555-0531',
            'pickup': '888 Law Office, Washington, DC 20001',
            'delivery': '111 Courthouse, Alexandria, VA 22301',
            'description': 'Legal documents and court filing equipment',
            'status': 'in_transit',
            'order_number': 'ORD-2025-5031'
        },
        {
            'name': 'Chloe Johnson',
            'email': 'chloe.johnson@email.com',
            'phone': '+1-555-0532',
            'pickup': '222 Beauty Salon Supply, Los Angeles, CA 90001',
            'delivery': '444 Spa Resort, Palm Springs, CA 92262',
            'description': 'Beauty and spa equipment supplies',
            'status': 'delivered',
            'order_number': 'ORD-2025-5032'
        },
        {
            'name': 'Andrew Davis',
            'email': 'andrew.davis@email.com',
            'phone': '+1-555-0533',
            'pickup': '555 Fitness Equipment Warehouse, Las Vegas, NV 89101',
            'delivery': '777 Gym Facility, Henderson, NV 89002',
            'description': 'Commercial fitness equipment and accessories',
            'status': 'pending',
            'order_number': 'ORD-2025-5033'
        },
        {
            'name': 'Penelope Brown',
            'email': 'penelope.brown@email.com',
            'phone': '+1-555-0534',
            'pickup': '888 Book Publishing House, New York, NY 10001',
            'delivery': '111 Library Distribution Center, Newark, NJ 07101',
            'description': 'Books and publishing materials',
            'status': 'confirmed',
            'order_number': 'ORD-2025-5034'
        },
        {
            'name': 'Christopher Garcia',
            'email': 'christopher.garcia@email.com',
            'phone': '+1-555-0535',
            'pickup': '111 Music Instrument Factory, Nashville, TN 37201',
            'delivery': '333 Music Store, Memphis, TN 38101',
            'description': 'Musical instruments and sound equipment',
            'status': 'in_transit',
            'order_number': 'ORD-2025-5035'
        },
        {
            'name': 'Riley Martinez',
            'email': 'riley.martinez@email.com',
            'phone': '+1-555-0536',
            'pickup': '444 Fashion Design Studio, Atlanta, GA 30301',
            'delivery': '666 Boutique Store, Savannah, GA 31401',
            'description': 'Designer clothing and fashion accessories',
            'status': 'delivered',
            'order_number': 'ORD-2025-5036'
        },
        {
            'name': 'Nora Anderson',
            'email': 'nora.anderson@email.com',
            'phone': '+1-555-0537',
            'pickup': '777 Renewable Energy Plant, Denver, CO 80201',
            'delivery': '999 Green Technology Center, Boulder, CO 80301',
            'description': 'Solar panels and renewable energy equipment',
            'status': 'pending',
            'order_number': 'ORD-2025-5037'
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
            package_weight=round(random.uniform(0.3, 100.0), 2),
            package_dimensions=f"{random.randint(3, 200)}x{random.randint(3, 200)}x{random.randint(2, 100)} cm",
            estimated_delivery=timezone.now() + timedelta(days=random.randint(1, 30)),
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
    print(f"   - Organic Farm Products")
    print(f"   - Solar Energy Systems")
    print(f"   - Biotech Research Equipment")
    print(f"   - Aerospace & Aviation Parts")
    print(f"   - Designer Fashion Items")
    print(f"   - Tech Startup Equipment")
    print(f"   - Fine Art & Gallery Pieces")
    print(f"   - Professional Audio Equipment")
    print(f"   - Luxury Jewelry & Gemstones")
    print(f"   - Automotive Parts & Accessories")
    print(f"   - Pharmaceutical Research Equipment")
    print(f"   - Consumer Electronics")
    print(f"   - Textiles & Fabrics")
    print(f"   - Custom Furniture")
    print(f"   - Educational Toys")
    print(f"   - Sports Equipment")
    print(f"   - Beauty & Cosmetics")
    print(f"   - Premium Wines & Spirits")
    print(f"   - Coffee & Beverages")
    print(f"   - Chocolate & Confectionery")
    print(f"   - Luxury Perfumes")
    print(f"   - Luxury Watches")
    print(f"   - Diamonds & Precious Stones")
    print(f"   - Leather Goods")
    print(f"   - Silk Fabrics")
    print(f"   - Artisan Crystal")
    print(f"   - Marine Research Equipment")
    print(f"   - Veterinary Equipment")
    print(f"   - Photography Equipment")
    print(f"   - Dance & Performance Gear")
    print(f"   - Legal Documents")
    print(f"   - Spa & Beauty Equipment")
    print(f"   - Fitness Equipment")
    print(f"   - Books & Publishing")
    print(f"   - Musical Instruments")
    print(f"   - Fashion Accessories")
    print(f"   - Renewable Energy Equipment")
    print(f"   - And many more diverse packages!")

if __name__ == '__main__':
    add_37_more_deliveries()
