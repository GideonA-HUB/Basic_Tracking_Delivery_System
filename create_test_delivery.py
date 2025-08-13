#!/usr/bin/env python
"""
Script to create a test delivery for demonstration purposes.
Run this script to add a sample delivery to the system.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from tracking.models import Delivery, DeliveryStatus
from django.contrib.auth.models import User
from django.utils import timezone

def create_test_delivery():
    """Create a test delivery with sample data"""
    
    # Get or create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Create test delivery
    delivery = Delivery.objects.create(
        order_number='TEST-2024-001',
        customer_name='John Doe',
        customer_email='john.doe@example.com',
        customer_phone='+1 (555) 123-4567',
        pickup_address='123 Warehouse St, New York, NY 10001',
        delivery_address='456 Customer Ave, Los Angeles, CA 90210',
        package_description='Electronics package containing laptop and accessories',
        package_weight=2.5,
        package_dimensions='40x30x20 cm',
        estimated_delivery=timezone.now() + timedelta(days=3),
        created_by=admin_user
    )
    
    # Create initial status update
    DeliveryStatus.objects.create(
        delivery=delivery,
        status='pending',
        description='Order received and pending confirmation'
    )
    
    # Create additional status updates for demonstration
    DeliveryStatus.objects.create(
        delivery=delivery,
        status='confirmed',
        location='New York Warehouse',
        description='Order confirmed and ready for shipping'
    )
    
    DeliveryStatus.objects.create(
        delivery=delivery,
        status='in_transit',
        location='Distribution Center',
        description='Package picked up and in transit to destination'
    )
    
    print(f"Test delivery created successfully!")
    print(f"Tracking Number: {delivery.tracking_number}")
    print(f"Tracking Secret: {delivery.tracking_secret}")
    print(f"Tracking URL: {delivery.get_tracking_url()}")
    print(f"Admin Dashboard: http://127.0.0.1:8000/dashboard/")
    print(f"Admin Login: http://127.0.0.1:8000/accounts/login/")
    print(f"Username: admin")
    print(f"Password: (the password you set earlier)")

if __name__ == '__main__':
    create_test_delivery()
