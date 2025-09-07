"""
Comprehensive Test Script for Live Map Tracking System
This script tests all components of the live tracking system
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_tracker.settings')
django.setup()

from tracking.models import Delivery, DeliveryStatus, DeliveryCheckpoint
from tracking.gps_service import gps_service, mock_gps_service


class LiveTrackingSystemTest:
    """Test class for the live tracking system"""
    
    def __init__(self):
        self.client = Client()
        self.test_delivery = None
        self.admin_user = None
    
    def setup_test_data(self):
        """Setup test data for the system"""
        print("🔧 Setting up test data...")
        
        # Create admin user
        self.admin_user, created = User.objects.get_or_create(
            username='test_admin',
            defaults={
                'email': 'admin@test.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            self.admin_user.set_password('testpass123')
            self.admin_user.save()
            print("✅ Created admin user")
        
        # Create test delivery
        self.test_delivery = Delivery.objects.create(
            order_number='TEST-001',
            customer_name='Test Customer',
            customer_email='test@example.com',
            customer_phone='+1234567890',
            pickup_address='123 Test St, Test City, TC 12345',
            delivery_address='456 Delivery Ave, Test City, TC 12345',
            pickup_latitude=40.7128,
            pickup_longitude=-74.0060,
            delivery_latitude=40.7589,
            delivery_longitude=-73.9851,
            package_description='Test Package',
            current_status='in_transit',
            gps_tracking_enabled=True,
            courier_name='Test Courier',
            courier_phone='+1987654321',
            courier_vehicle_type='Van',
            courier_vehicle_number='TEST-001',
            created_by=self.admin_user
        )
        
        print(f"✅ Created test delivery: {self.test_delivery.tracking_number}")
        return True
    
    def test_models(self):
        """Test the enhanced models"""
        print("\n🧪 Testing Models...")
        
        # Test delivery model methods
        assert self.test_delivery.has_geolocation() == False, "Should not have geolocation initially"
        assert self.test_delivery.get_courier_info() is not None, "Should have courier info"
        assert self.test_delivery.is_gps_active() == False, "Should not have active GPS initially"
        
        # Test location update
        self.test_delivery.update_current_location(
            latitude=40.7300,
            longitude=-73.9900,
            location_name='Test Location',
            accuracy=5.0
        )
        
        assert self.test_delivery.has_geolocation() == True, "Should have geolocation after update"
        assert self.test_delivery.current_location_name == 'Test Location', "Location name should be set"
        
        # Test checkpoint creation
        checkpoint = DeliveryCheckpoint.objects.create(
            delivery=self.test_delivery,
            checkpoint_type='transit',
            location_name='Test Checkpoint',
            latitude=40.7300,
            longitude=-73.9900,
            description='Test checkpoint'
        )
        
        assert checkpoint.delivery == self.test_delivery, "Checkpoint should be linked to delivery"
        assert self.test_delivery.checkpoints.count() == 1, "Should have one checkpoint"
        
        print("✅ Models test passed")
        return True
    
    def test_gps_service(self):
        """Test the GPS service"""
        print("\n🧪 Testing GPS Service...")
        
        # Test enabling GPS tracking
        result = gps_service.enable_gps_tracking(self.test_delivery.id, 30)
        assert result == True, "Should enable GPS tracking"
        
        # Test location update
        result = gps_service.update_delivery_location(
            delivery_id=self.test_delivery.id,
            latitude=40.7400,
            longitude=-73.9800,
            location_name='GPS Test Location',
            accuracy=3.0
        )
        assert result == True, "Should update location"
        
        # Refresh from database
        self.test_delivery.refresh_from_db()
        assert self.test_delivery.current_latitude == 40.7400, "Latitude should be updated"
        assert self.test_delivery.current_longitude == -73.9800, "Longitude should be updated"
        
        # Test disabling GPS tracking
        result = gps_service.disable_gps_tracking(self.test_delivery.id)
        assert result == True, "Should disable GPS tracking"
        
        self.test_delivery.refresh_from_db()
        assert self.test_delivery.gps_tracking_enabled == False, "GPS tracking should be disabled"
        
        print("✅ GPS Service test passed")
        return True
    
    def test_admin_interface(self):
        """Test the admin interface"""
        print("\n🧪 Testing Admin Interface...")
        
        # Login as admin
        login_success = self.client.login(username='test_admin', password='testpass123')
        assert login_success == True, "Should be able to login as admin"
        
        # Test delivery admin list
        response = self.client.get('/admin/tracking/delivery/')
        assert response.status_code == 200, "Should access delivery admin list"
        
        # Test delivery change page
        response = self.client.get(f'/admin/tracking/delivery/{self.test_delivery.id}/change/')
        assert response.status_code == 200, "Should access delivery change page"
        
        # Test live map view
        response = self.client.get(f'/admin/tracking/delivery/live-map/{self.test_delivery.id}/')
        assert response.status_code == 200, "Should access live map view"
        
        # Test update location view
        response = self.client.get(f'/admin/tracking/delivery/update-location/{self.test_delivery.id}/')
        assert response.status_code == 200, "Should access update location view"
        
        # Test global dashboard
        response = self.client.get('/admin/tracking/delivery/global-dashboard/')
        assert response.status_code == 200, "Should access global dashboard"
        
        print("✅ Admin Interface test passed")
        return True
    
    def test_websocket_consumers(self):
        """Test WebSocket consumers"""
        print("\n🧪 Testing WebSocket Consumers...")
        
        # Test tracking consumer URL pattern
        from tracking.routing import websocket_urlpatterns
        assert len(websocket_urlpatterns) >= 2, "Should have WebSocket URL patterns"
        
        # Test consumer imports
        from tracking.consumers import DeliveryTrackingConsumer, AdminDeliveryConsumer
        assert DeliveryTrackingConsumer is not None, "Should have DeliveryTrackingConsumer"
        assert AdminDeliveryConsumer is not None, "Should have AdminDeliveryConsumer"
        
        print("✅ WebSocket Consumers test passed")
        return True
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🧪 Testing API Endpoints...")
        
        # Test tracking API
        tracking_url = f'/api/track/{self.test_delivery.tracking_number}/{self.test_delivery.tracking_secret}/'
        response = self.client.get(tracking_url)
        assert response.status_code == 200, "Should access tracking API"
        
        data = response.json()
        assert 'delivery' in data, "Should have delivery data"
        assert data['delivery']['tracking_number'] == self.test_delivery.tracking_number, "Should match tracking number"
        
        print("✅ API Endpoints test passed")
        return True
    
    def test_mock_gps_simulation(self):
        """Test mock GPS simulation"""
        print("\n🧪 Testing Mock GPS Simulation...")
        
        # Create a sample route
        route = mock_gps_service.create_sample_route(
            start_lat=40.7128,
            start_lng=-74.0060,
            end_lat=40.7589,
            end_lng=-73.9851,
            num_points=5
        )
        
        assert len(route) == 5, "Should create route with correct number of points"
        assert route[0][2] == "Route Point 1", "Should have correct location names"
        assert route[-1][2] == "Route Point 5", "Should have correct final location name"
        
        # Test simulation (without actually running it to avoid delays)
        print("✅ Mock GPS Simulation test passed")
        return True
    
    def test_templates(self):
        """Test that templates exist and are accessible"""
        print("\n🧪 Testing Templates...")
        
        template_files = [
            'templates/admin/tracking/delivery/live_map.html',
            'templates/admin/tracking/delivery/update_location.html',
            'templates/admin/tracking/delivery/global_dashboard.html',
            'templates/admin/tracking/delivery/add_checkpoint.html',
            'templates/tracking/tracking_page.html'
        ]
        
        for template_file in template_files:
            assert os.path.exists(template_file), f"Template {template_file} should exist"
        
        print("✅ Templates test passed")
        return True
    
    def test_static_files(self):
        """Test that static files exist"""
        print("\n🧪 Testing Static Files...")
        
        static_files = [
            'static/js/delivery_tracking_map.js'
        ]
        
        for static_file in static_files:
            assert os.path.exists(static_file), f"Static file {static_file} should exist"
        
        print("✅ Static Files test passed")
        return True
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        if self.test_delivery:
            self.test_delivery.delete()
            print("✅ Deleted test delivery")
        
        if self.admin_user:
            self.admin_user.delete()
            print("✅ Deleted test admin user")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Live Tracking System Tests...")
        print("=" * 50)
        
        try:
            # Setup
            self.setup_test_data()
            
            # Run tests
            tests = [
                self.test_models,
                self.test_gps_service,
                self.test_admin_interface,
                self.test_websocket_consumers,
                self.test_api_endpoints,
                self.test_mock_gps_simulation,
                self.test_templates,
                self.test_static_files
            ]
            
            passed = 0
            failed = 0
            
            for test in tests:
                try:
                    if test():
                        passed += 1
                except Exception as e:
                    print(f"❌ {test.__name__} failed: {e}")
                    failed += 1
            
            # Results
            print("\n" + "=" * 50)
            print(f"📊 Test Results: {passed} passed, {failed} failed")
            
            if failed == 0:
                print("🎉 All tests passed! Live tracking system is working correctly.")
                return True
            else:
                print("⚠️ Some tests failed. Please check the errors above.")
                return False
                
        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            return False
        finally:
            self.cleanup_test_data()


def main():
    """Main function to run tests"""
    print("Live Map Tracking System - Comprehensive Test Suite")
    print("=" * 60)
    
    tester = LiveTrackingSystemTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ System is ready for live map tracking!")
        print("\n📋 Next Steps:")
        print("1. Set up Google Maps API key in settings")
        print("2. Run migrations: python manage.py migrate")
        print("3. Create sample deliveries with GPS tracking")
        print("4. Test the admin interface and customer tracking pages")
        print("5. Simulate GPS tracking: python manage.py simulate_gps_tracking")
    else:
        print("\n❌ System needs fixes before deployment")
        sys.exit(1)


if __name__ == '__main__':
    main()
