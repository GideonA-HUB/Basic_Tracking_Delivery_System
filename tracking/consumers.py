import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Delivery, DeliveryStatus
from django.utils import timezone

logger = logging.getLogger(__name__)

class DeliveryTrackingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time delivery tracking"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            self.tracking_number = self.scope['url_route']['kwargs']['tracking_number']
            self.tracking_secret = self.scope['url_route']['kwargs']['tracking_secret']
            self.room_group_name = f'delivery_tracking_{self.tracking_number}'
            
            logger.info(f"🔌 Attempting WebSocket connection for tracking: {self.tracking_number}")
            
            # Verify tracking credentials
            delivery = await self.get_delivery()
            if not delivery:
                logger.warning(f"❌ Delivery not found for tracking: {self.tracking_number}")
                await self.close()
                return
            
            # Check if tracking link is expired
            if delivery.is_tracking_link_expired():
                logger.warning(f"❌ Tracking link expired for: {self.tracking_number}")
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'This tracking link has expired'
                }))
                await self.close()
                return
            
            # Join room group
            try:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                logger.info(f"✅ Joined room group: {self.room_group_name}")
            except Exception as e:
                logger.error(f"❌ Failed to join room group: {e}")
                # Continue anyway - WebSocket can still work without channel layer
            
            await self.accept()
            
            # Send initial tracking data
            await self.send_initial_data()
            
            logger.info(f"✅ Delivery tracking WebSocket connected: {self.tracking_number}")
            
        except Exception as e:
            logger.error(f"❌ Error in WebSocket connect: {e}")
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"❌ Error disconnecting from room group: {e}")
        
        logger.info(f"❌ Delivery tracking WebSocket disconnected: {self.tracking_number} (code: {close_code})")
    
    async def receive(self, text_data):
        """Handle WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'get_tracking_data':
                await self.send_initial_data()
            elif message_type == 'location_update':
                # Handle location updates from admin/courier
                await self.handle_location_update(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in WebSocket receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def send_initial_data(self):
        """Send initial tracking data to client"""
        delivery = await self.get_delivery()
        if not delivery:
            return
        
        # Get tracking data
        tracking_data = await self.get_tracking_data()
        
        await self.send(text_data=json.dumps({
            'type': 'tracking_data',
            'data': tracking_data
        }))
    
    async def handle_location_update(self, data):
        """Handle location updates from admin/courier"""
        try:
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            location_name = data.get('location_name')
            accuracy = data.get('accuracy')
            
            if not latitude or not longitude:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Latitude and longitude are required'
                }))
                return
            
            # Update delivery location
            delivery = await self.get_delivery()
            if delivery:
                await self.update_delivery_location(
                    delivery, latitude, longitude, location_name, accuracy
                )
                
                # Broadcast update to all connected clients
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'location_update',
                        'latitude': latitude,
                        'longitude': longitude,
                        'location_name': location_name,
                        'accuracy': accuracy,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
                await self.send(text_data=json.dumps({
                    'type': 'success',
                    'message': 'Location updated successfully'
                }))
            
        except Exception as e:
            logger.error(f"Error handling location update: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to update location'
            }))
    
    async def location_update(self, event):
        """Handle location update broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'location_name': event['location_name'],
            'accuracy': event['accuracy'],
            'timestamp': event['timestamp']
        }))
    
    async def status_update(self, event):
        """Handle status update broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status'],
            'description': event['description'],
            'location': event['location'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def get_delivery(self):
        """Get delivery by tracking number and secret"""
        try:
            return Delivery.objects.get(
                tracking_number=self.tracking_number,
                tracking_secret=self.tracking_secret
            )
        except Delivery.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_tracking_data(self):
        """Get comprehensive tracking data"""
        try:
            delivery = Delivery.objects.get(
                tracking_number=self.tracking_number,
                tracking_secret=self.tracking_secret
            )
            
            # Get status updates with geolocation
            status_updates = []
            for status in delivery.status_updates.all():
                status_data = {
                    'id': status.id,
                    'status': status.status,
                    'status_display': delivery.get_status_display(),
                    'location': status.location,
                    'description': status.description,
                    'timestamp': status.timestamp.isoformat(),
                    'formatted_timestamp': status.timestamp.strftime('%B %d, %Y at %I:%M %p'),
                    'latitude': float(status.latitude) if status.latitude else None,
                    'longitude': float(status.longitude) if status.longitude else None,
                    'location_name': status.location_name,
                    'accuracy': float(status.accuracy) if status.accuracy else None
                }
                status_updates.append(status_data)
            
            # Get checkpoints
            checkpoints = []
            for checkpoint in delivery.checkpoints.all()[:10]:  # Last 10 checkpoints
                checkpoint_data = {
                    'id': checkpoint.id,
                    'checkpoint_type': checkpoint.checkpoint_type,
                    'checkpoint_type_display': checkpoint.get_checkpoint_type_display(),
                    'location_name': checkpoint.location_name,
                    'description': checkpoint.description,
                    'latitude': float(checkpoint.latitude) if checkpoint.latitude else None,
                    'longitude': float(checkpoint.longitude) if checkpoint.longitude else None,
                    'accuracy': float(checkpoint.accuracy) if checkpoint.accuracy else None,
                    'timestamp': checkpoint.timestamp.isoformat(),
                    'formatted_timestamp': checkpoint.timestamp.strftime('%B %d, %Y at %I:%M %p'),
                    'courier_notes': checkpoint.courier_notes,
                    'customer_notified': checkpoint.customer_notified
                }
                checkpoints.append(checkpoint_data)
            
            # Calculate progress percentage
            status_order = {
                'pending': 0,
                'confirmed': 1,
                'in_transit': 2,
                'out_for_delivery': 3,
                'delivered': 4,
                'failed': 5,
                'returned': 6
            }
            
            current_status_order = status_order.get(delivery.current_status, 0)
            total_statuses = len(status_order)
            progress_percentage = (current_status_order / (total_statuses - 1)) * 100
            
            return {
                'delivery': {
                    'id': delivery.id,
                    'tracking_number': delivery.tracking_number,
                    'order_number': delivery.order_number,
                    'customer_name': delivery.customer_name,
                    'customer_email': delivery.customer_email,
                    'customer_phone': delivery.customer_phone,
                    'package_description': delivery.package_description,
                    'package_weight': float(delivery.package_weight) if delivery.package_weight else None,
                    'package_dimensions': delivery.package_dimensions,
                    'pickup_address': delivery.pickup_address,
                    'delivery_address': delivery.delivery_address,
                    'current_status': delivery.current_status,
                    'current_status_display': delivery.get_current_status_display(),
                    'estimated_delivery': delivery.estimated_delivery.isoformat() if delivery.estimated_delivery else None,
                    'actual_delivery': delivery.actual_delivery.isoformat() if delivery.actual_delivery else None,
                    'created_at': delivery.created_at.isoformat(),
                    'updated_at': delivery.updated_at.isoformat(),
                    'progress_percentage': round(progress_percentage, 1),
                    'has_geolocation': delivery.has_geolocation(),
                    'is_gps_active': delivery.is_gps_active(),
                    'gps_tracking_enabled': delivery.gps_tracking_enabled,
                    'current_location': delivery.get_current_location_dict(),
                    'pickup_location': delivery.get_pickup_location_dict(),
                    'delivery_location': delivery.get_delivery_location_dict(),
                    'courier_info': delivery.get_courier_info()
                },
                'status_updates': status_updates,
                'checkpoints': checkpoints
            }
            
        except Delivery.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_delivery_location(self, delivery, latitude, longitude, location_name=None, accuracy=None):
        """Update delivery location"""
        delivery.update_current_location(
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            accuracy=accuracy
        )


class AdminDeliveryConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for admin delivery monitoring"""
    
    async def connect(self):
        """Handle admin WebSocket connection"""
        self.user = self.scope['user']
        
        # Check if user is staff
        if not self.user.is_authenticated or not self.user.is_staff:
            await self.close()
            return
        
        self.room_group_name = 'admin_delivery_monitoring'
        
        # Join admin room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial data
        await self.send_initial_admin_data()
        
        logger.info(f"✅ Admin delivery monitoring WebSocket connected: {self.user.username}")
    
    async def disconnect(self, close_code):
        """Handle admin WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"❌ Admin delivery monitoring WebSocket disconnected: {self.user.username}")
    
    async def receive(self, text_data):
        """Handle admin WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'get_all_deliveries':
                await self.send_initial_admin_data()
            elif message_type == 'update_delivery_location':
                await self.handle_admin_location_update(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in admin WebSocket receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def send_initial_admin_data(self):
        """Send initial admin data"""
        deliveries_data = await self.get_all_deliveries_data()
        
        await self.send(text_data=json.dumps({
            'type': 'admin_data',
            'deliveries': deliveries_data
        }))
    
    async def handle_admin_location_update(self, data):
        """Handle location update from admin"""
        try:
            delivery_id = data.get('delivery_id')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            location_name = data.get('location_name')
            accuracy = data.get('accuracy')
            
            if not delivery_id or not latitude or not longitude:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Delivery ID, latitude and longitude are required'
                }))
                return
            
            # Update delivery location
            success = await self.update_delivery_location_by_id(
                delivery_id, latitude, longitude, location_name, accuracy
            )
            
            if success:
                # Broadcast to admin room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'delivery_location_updated',
                        'delivery_id': delivery_id,
                        'latitude': latitude,
                        'longitude': longitude,
                        'location_name': location_name,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
                # Broadcast to specific delivery tracking room
                delivery = await self.get_delivery_by_id(delivery_id)
                if delivery:
                    await self.channel_layer.group_send(
                        f'delivery_tracking_{delivery.tracking_number}',
                        {
                            'type': 'location_update',
                            'latitude': latitude,
                            'longitude': longitude,
                            'location_name': location_name,
                            'accuracy': accuracy,
                            'timestamp': timezone.now().isoformat()
                        }
                    )
                
                await self.send(text_data=json.dumps({
                    'type': 'success',
                    'message': 'Location updated successfully'
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Failed to update location'
                }))
            
        except Exception as e:
            logger.error(f"Error handling admin location update: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to update location'
            }))
    
    async def delivery_location_updated(self, event):
        """Handle delivery location update broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'delivery_location_updated',
            'delivery_id': event['delivery_id'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'location_name': event['location_name'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def get_all_deliveries_data(self):
        """Get all deliveries data for admin dashboard"""
        deliveries = Delivery.objects.filter(
            current_status__in=['confirmed', 'in_transit', 'out_for_delivery']
        ).select_related('created_by')
        
        deliveries_data = []
        for delivery in deliveries:
            delivery_data = {
                'id': delivery.id,
                'tracking_number': delivery.tracking_number,
                'order_number': delivery.order_number,
                'customer_name': delivery.customer_name,
                'current_status': delivery.current_status,
                'current_status_display': delivery.get_current_status_display(),
                'package_description': delivery.package_description,
                'pickup_address': delivery.pickup_address,
                'delivery_address': delivery.delivery_address,
                'estimated_delivery': delivery.estimated_delivery.isoformat() if delivery.estimated_delivery else None,
                'has_geolocation': delivery.has_geolocation(),
                'current_location': delivery.get_current_location_dict(),
                'pickup_location': delivery.get_pickup_location_dict(),
                'delivery_location': delivery.get_delivery_location_dict(),
                'created_at': delivery.created_at.isoformat(),
                'updated_at': delivery.updated_at.isoformat()
            }
            deliveries_data.append(delivery_data)
        
        return deliveries_data
    
    @database_sync_to_async
    def get_delivery_by_id(self, delivery_id):
        """Get delivery by ID"""
        try:
            return Delivery.objects.get(id=delivery_id)
        except Delivery.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_delivery_location_by_id(self, delivery_id, latitude, longitude, location_name=None, accuracy=None):
        """Update delivery location by ID"""
        try:
            delivery = Delivery.objects.get(id=delivery_id)
            delivery.update_current_location(
                latitude=latitude,
                longitude=longitude,
                location_name=location_name,
                accuracy=accuracy
            )
            return True
        except Delivery.DoesNotExist:
            return False
