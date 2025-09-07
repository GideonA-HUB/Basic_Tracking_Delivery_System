"""
Simple test for the live tracking system
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from tracking.models import Delivery, DeliveryCheckpoint
from tracking.gps_service import gps_service
from django.contrib.auth.models import User

def test_system():
    print("Testing Live Tracking System...")
    
    try:
        # Create a test user
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'is_staff': True}
        )
        
        # Create a test delivery
        delivery = Delivery.objects.create(
            order_number='TEST-001',
            customer_name='Test Customer',
            pickup_address='123 Test St',
            delivery_address='456 Test Ave',
            package_description='Test Package',
            created_by=user
        )
        
        print(f"Test delivery created: {delivery.tracking_number}")
        
        # Test GPS service
        gps_service.enable_gps_tracking(delivery.id)
        print("GPS tracking enabled")
        
        gps_service.update_delivery_location(
            delivery.id, 40.7128, -74.0060, "Test Location"
        )
        print("Location updated via GPS service")
        
        # Test checkpoint creation
        checkpoint = DeliveryCheckpoint.objects.create(
            delivery=delivery,
            checkpoint_type='transit',
            location_name='Test Checkpoint',
            latitude=40.7128,
            longitude=-74.0060
        )
        print("Checkpoint created")
        
        # Cleanup
        delivery.delete()
        user.delete()
        print("Test data cleaned up")
        
        print("System test successful!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == '__main__':
    test_system()
