"""
GPS Integration Service for Automatic Location Updates
This service handles automatic GPS location updates for deliveries
"""

import logging
import asyncio
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from .models import Delivery, DeliveryCheckpoint
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class GPSTrackingService:
    """Service for managing GPS tracking and automatic location updates"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def enable_gps_tracking(self, delivery_id, update_frequency=30):
        """Enable GPS tracking for a delivery"""
        try:
            delivery = Delivery.objects.get(id=delivery_id)
            delivery.gps_tracking_enabled = True
            delivery.location_update_frequency = update_frequency
            delivery.save()
            
            logger.info(f"GPS tracking enabled for delivery {delivery.tracking_number}")
            return True
        except Delivery.DoesNotExist:
            logger.error(f"Delivery {delivery_id} not found")
            return False
    
    def disable_gps_tracking(self, delivery_id):
        """Disable GPS tracking for a delivery"""
        try:
            delivery = Delivery.objects.get(id=delivery_id)
            delivery.gps_tracking_enabled = False
            delivery.save()
            
            logger.info(f"GPS tracking disabled for delivery {delivery.tracking_number}")
            return True
        except Delivery.DoesNotExist:
            logger.error(f"Delivery {delivery_id} not found")
            return False
    
    def update_delivery_location(self, delivery_id, latitude, longitude, location_name=None, accuracy=None):
        """Update delivery location and broadcast to WebSocket clients"""
        try:
            with transaction.atomic():
                delivery = Delivery.objects.select_for_update().get(id=delivery_id)
                
                # Update delivery location
                delivery.update_current_location(
                    latitude=latitude,
                    longitude=longitude,
                    location_name=location_name,
                    accuracy=accuracy
                )
                
                # Create checkpoint if significant movement
                if self._should_create_checkpoint(delivery, latitude, longitude):
                    DeliveryCheckpoint.objects.create(
                        delivery=delivery,
                        checkpoint_type='transit',
                        location_name=location_name or f"GPS Location",
                        latitude=latitude,
                        longitude=longitude,
                        accuracy=accuracy,
                        description=f"Automatic GPS update: {location_name or 'GPS coordinates'}"
                    )
                
                # Broadcast location update to WebSocket clients
                self._broadcast_location_update(delivery, latitude, longitude, location_name, accuracy)
                
                logger.info(f"Location updated for delivery {delivery.tracking_number}: {latitude}, {longitude}")
                return True
                
        except Delivery.DoesNotExist:
            logger.error(f"Delivery {delivery_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error updating location for delivery {delivery_id}: {e}")
            return False
    
    def _should_create_checkpoint(self, delivery, latitude, longitude):
        """Determine if a checkpoint should be created based on movement"""
        if not delivery.current_latitude or not delivery.current_longitude:
            return True
        
        # Calculate distance from last location
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            """Calculate the great circle distance between two points on earth"""
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # Radius of earth in kilometers
            return c * r
        
        distance = haversine(
            float(delivery.current_longitude),
            float(delivery.current_latitude),
            longitude,
            latitude
        )
        
        # Create checkpoint if moved more than 100 meters
        return distance > 0.1
    
    def _broadcast_location_update(self, delivery, latitude, longitude, location_name, accuracy):
        """Broadcast location update to WebSocket clients"""
        try:
            # Broadcast to customer tracking room
            customer_room = f'delivery_tracking_{delivery.tracking_number}'
            async_to_sync(self.channel_layer.group_send)(
                customer_room,
                {
                    'type': 'location_update',
                    'latitude': latitude,
                    'longitude': longitude,
                    'location_name': location_name,
                    'accuracy': accuracy,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            # Broadcast to admin monitoring room
            admin_room = 'admin_delivery_monitoring'
            async_to_sync(self.channel_layer.group_send)(
                admin_room,
                {
                    'type': 'delivery_location_updated',
                    'delivery_id': delivery.id,
                    'latitude': latitude,
                    'longitude': longitude,
                    'location_name': location_name,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error broadcasting location update: {e}")
    
    def get_active_gps_deliveries(self):
        """Get all deliveries with active GPS tracking"""
        return Delivery.objects.filter(
            gps_tracking_enabled=True,
            current_status__in=['confirmed', 'in_transit', 'out_for_delivery']
        )
    
    def cleanup_old_checkpoints(self, days=30):
        """Clean up old checkpoints to prevent database bloat"""
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = DeliveryCheckpoint.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old checkpoints")
        return deleted_count


class MockGPSService:
    """Mock GPS service for testing and development"""
    
    def __init__(self):
        self.gps_service = GPSTrackingService()
    
    def simulate_delivery_movement(self, delivery_id, route_points):
        """Simulate delivery movement along a route"""
        try:
            delivery = Delivery.objects.get(id=delivery_id)
            
            for i, point in enumerate(route_points):
                latitude, longitude, location_name = point
                
                # Update location
                self.gps_service.update_delivery_location(
                    delivery_id=delivery_id,
                    latitude=latitude,
                    longitude=longitude,
                    location_name=location_name,
                    accuracy=5.0  # Mock accuracy
                )
                
                # Wait between updates (simulate real movement)
                if i < len(route_points) - 1:
                    import time
                    time.sleep(2)  # 2 seconds between updates
                    
        except Delivery.DoesNotExist:
            logger.error(f"Delivery {delivery_id} not found for simulation")
        except Exception as e:
            logger.error(f"Error simulating delivery movement: {e}")
    
    def create_sample_route(self, start_lat, start_lng, end_lat, end_lng, num_points=10):
        """Create a sample route between two points"""
        import random
        
        route = []
        
        # Generate intermediate points
        for i in range(num_points):
            # Linear interpolation with some randomness
            ratio = i / (num_points - 1)
            lat = start_lat + (end_lat - start_lat) * ratio
            lng = start_lng + (end_lng - start_lng) * ratio
            
            # Add some randomness to simulate real road movement
            lat += random.uniform(-0.001, 0.001)
            lng += random.uniform(-0.001, 0.001)
            
            location_name = f"Route Point {i+1}"
            route.append((lat, lng, location_name))
        
        return route


# Global GPS service instance
gps_service = GPSTrackingService()
mock_gps_service = MockGPSService()
