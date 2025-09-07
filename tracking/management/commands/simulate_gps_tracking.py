"""
Management command to simulate GPS tracking for deliveries
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from tracking.models import Delivery
from tracking.gps_service import mock_gps_service
import random


class Command(BaseCommand):
    help = 'Simulate GPS tracking for active deliveries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delivery-id',
            type=int,
            help='Specific delivery ID to simulate (optional)',
        )
        parser.add_argument(
            '--duration',
            type=int,
            default=60,
            help='Simulation duration in seconds (default: 60)',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=10,
            help='Update interval in seconds (default: 10)',
        )

    def handle(self, *args, **options):
        delivery_id = options.get('delivery_id')
        duration = options.get('duration')
        interval = options.get('interval')

        if delivery_id:
            # Simulate specific delivery
            try:
                delivery = Delivery.objects.get(id=delivery_id)
                self.simulate_single_delivery(delivery, duration, interval)
            except Delivery.DoesNotExist:
                raise CommandError(f'Delivery with ID {delivery_id} does not exist')
        else:
            # Simulate all active deliveries
            active_deliveries = Delivery.objects.filter(
                current_status__in=['confirmed', 'in_transit', 'out_for_delivery'],
                gps_tracking_enabled=True
            )
            
            if not active_deliveries.exists():
                self.stdout.write(
                    self.style.WARNING('No active deliveries with GPS tracking enabled found')
                )
                return
            
            self.stdout.write(f'Found {active_deliveries.count()} active deliveries')
            
            for delivery in active_deliveries:
                self.simulate_single_delivery(delivery, duration, interval)

    def simulate_single_delivery(self, delivery, duration, interval):
        """Simulate GPS tracking for a single delivery"""
        self.stdout.write(f'Simulating GPS tracking for delivery {delivery.tracking_number}')
        
        # Create a route from pickup to delivery location
        if delivery.pickup_latitude and delivery.pickup_longitude and delivery.delivery_latitude and delivery.delivery_longitude:
            route = mock_gps_service.create_sample_route(
                float(delivery.pickup_latitude),
                float(delivery.pickup_longitude),
                float(delivery.delivery_latitude),
                float(delivery.delivery_longitude),
                num_points=max(5, duration // interval)
            )
            
            # Add pickup and delivery points
            route.insert(0, (
                float(delivery.pickup_latitude),
                float(delivery.pickup_longitude),
                'Pickup Location'
            ))
            route.append((
                float(delivery.delivery_latitude),
                float(delivery.delivery_longitude),
                'Delivery Location'
            ))
            
            # Simulate movement
            mock_gps_service.simulate_delivery_movement(delivery.id, route)
            
            self.stdout.write(
                self.style.SUCCESS(f'Completed GPS simulation for {delivery.tracking_number}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Delivery {delivery.tracking_number} missing location data')
            )

    def create_sample_deliveries_with_gps(self):
        """Create sample deliveries with GPS tracking enabled"""
        from tracking.models import Delivery
        from django.contrib.auth.models import User
        
        # Get or create a user for the deliveries
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )
        
        sample_deliveries = [
            {
                'order_number': 'ORD-001',
                'customer_name': 'John Doe',
                'customer_email': 'john@example.com',
                'customer_phone': '+1234567890',
                'pickup_address': '123 Main St, New York, NY 10001',
                'delivery_address': '456 Broadway, New York, NY 10013',
                'pickup_latitude': 40.7128,
                'pickup_longitude': -74.0060,
                'delivery_latitude': 40.7589,
                'delivery_longitude': -73.9851,
                'package_description': 'Electronics Package',
                'current_status': 'in_transit',
                'gps_tracking_enabled': True,
                'courier_name': 'Mike Johnson',
                'courier_phone': '+1987654321',
                'courier_vehicle_type': 'Van',
                'courier_vehicle_number': 'VAN-001',
                'created_by': user
            },
            {
                'order_number': 'ORD-002',
                'customer_name': 'Jane Smith',
                'customer_email': 'jane@example.com',
                'customer_phone': '+1234567891',
                'pickup_address': '789 5th Ave, New York, NY 10022',
                'delivery_address': '321 Park Ave, New York, NY 10010',
                'pickup_latitude': 40.7505,
                'pickup_longitude': -73.9934,
                'delivery_latitude': 40.7489,
                'delivery_longitude': -73.9857,
                'package_description': 'Clothing Package',
                'current_status': 'out_for_delivery',
                'gps_tracking_enabled': True,
                'courier_name': 'Sarah Wilson',
                'courier_phone': '+1987654322',
                'courier_vehicle_type': 'Motorcycle',
                'courier_vehicle_number': 'MC-002',
                'created_by': user
            }
        ]
        
        created_deliveries = []
        for delivery_data in sample_deliveries:
            delivery, created = Delivery.objects.get_or_create(
                order_number=delivery_data['order_number'],
                defaults=delivery_data
            )
            if created:
                created_deliveries.append(delivery)
                self.stdout.write(f'Created delivery: {delivery.tracking_number}')
        
        return created_deliveries
