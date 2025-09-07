from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import Delivery, DeliveryStatus
from .serializers import (
    DeliverySerializer, DeliveryCreateSerializer, DeliveryStatusSerializer,
    DeliveryStatusCreateSerializer, TrackingResponseSerializer
)
from .email_utils import test_email_configuration
from django.db import models


class IsStaffUser(permissions.BasePermission):
    """Custom permission to allow access only to staff users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


@method_decorator(csrf_exempt, name='dispatch')
class DeliveryViewSet(viewsets.ModelViewSet):
    """ViewSet for delivery management"""
    
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsStaffUser]  # Require staff authentication
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return DeliveryCreateSerializer
        return DeliverySerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = Delivery.objects.all()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(current_status=status_filter)
        
        # Filter by customer name if provided
        customer_name = self.request.query_params.get('customer_name', None)
        if customer_name:
            queryset = queryset.filter(customer_name__icontains=customer_name)
        
        # Filter by tracking number if provided
        tracking_number = self.request.query_params.get('tracking_number', None)
        if tracking_number:
            queryset = queryset.filter(tracking_number__icontains=tracking_number)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update delivery status"""
        delivery = self.get_object()
        serializer = DeliveryStatusCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Set the delivery for the status update
            status_update = serializer.save(delivery=delivery)
            
            # Update delivery timestamps based on status
            if status_update.status == 'delivered':
                delivery.actual_delivery = timezone.now()
                delivery.save()
            
            return Response({
                'message': 'Status updated successfully',
                'status_update': DeliveryStatusSerializer(status_update).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def tracking_info(self, request, pk=None):
        """Get tracking information for a delivery"""
        delivery = self.get_object()
        serializer = TrackingResponseSerializer(delivery, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def extend_tracking_link(self, request, pk=None):
        """Extend the tracking link expiry"""
        delivery = self.get_object()
        
        # Extend by 30 days
        delivery.tracking_link_expires = timezone.now() + timezone.timedelta(days=30)
        delivery.save()
        
        return Response({
            'message': 'Tracking link extended successfully',
            'new_expiry': delivery.tracking_link_expires
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class DeliveryStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for delivery status updates"""
    
    queryset = DeliveryStatus.objects.all()
    serializer_class = DeliveryStatusSerializer
    permission_classes = [IsStaffUser]
    
    def get_queryset(self):
        """Filter status updates by delivery"""
        queryset = DeliveryStatus.objects.all()
        
        delivery_id = self.request.query_params.get('delivery_id', None)
        if delivery_id:
            queryset = queryset.filter(delivery_id=delivery_id)
        
        return queryset


class TrackingAPIView(APIView):
    """Public API for tracking deliveries"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, tracking_number, tracking_secret):
        """Get tracking information for a delivery"""
        try:
            delivery = Delivery.objects.get(
                tracking_number=tracking_number,
                tracking_secret=tracking_secret
            )
            
            # Check if tracking link has expired
            if delivery.is_tracking_link_expired():
                return Response({
                    'error': 'This tracking link has expired',
                    'expired_at': delivery.tracking_link_expires
                }, status=status.HTTP_410_GONE)
            
            serializer = TrackingResponseSerializer(delivery, context={'request': request})
            return Response(serializer.data)
            
        except Delivery.DoesNotExist:
            return Response({
                'error': 'Delivery not found or invalid tracking information'
            }, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class DeliverySearchAPIView(APIView):
    """API for searching deliveries"""
    
    permission_classes = [IsStaffUser]
    
    def get(self, request):
        """Search deliveries by various criteria"""
        query = request.query_params.get('q', '')
        status_filter = request.query_params.get('status', '')
        
        queryset = Delivery.objects.all()
        
        if query:
            queryset = queryset.filter(
                models.Q(tracking_number__icontains=query) |
                models.Q(order_number__icontains=query) |
                models.Q(customer_name__icontains=query)
            )
        
        if status_filter:
            queryset = queryset.filter(current_status=status_filter)
        
        serializer = DeliverySerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class DeliveryStatsAPIView(APIView):
    """API for delivery statistics"""
    
    permission_classes = [IsStaffUser]
    
    def get(self, request):
        """Get delivery statistics"""
        total_deliveries = Delivery.objects.count()
        pending_deliveries = Delivery.objects.filter(current_status='pending').count()
        in_transit_deliveries = Delivery.objects.filter(current_status='in_transit').count()
        delivered_deliveries = Delivery.objects.filter(current_status='delivered').count()
        failed_deliveries = Delivery.objects.filter(current_status='failed').count()
        
        # Recent deliveries (last 7 days)
        from datetime import timedelta
        recent_deliveries = Delivery.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        return Response({
            'total_deliveries': total_deliveries,
            'pending_deliveries': pending_deliveries,
            'in_transit_deliveries': in_transit_deliveries,
            'delivered_deliveries': delivered_deliveries,
            'failed_deliveries': failed_deliveries,
            'recent_deliveries': recent_deliveries,
        })


@method_decorator(csrf_exempt, name='dispatch')
class EmailTestView(APIView):
    """Test email configuration endpoint for production"""
    
    def get(self, request):
        """Test email configuration"""
        try:
            # Test email configuration
            success = test_email_configuration()
            
            return JsonResponse({
                'status': 'success' if success else 'failed',
                'message': 'Email test completed',
                'email_settings': {
                    'host': settings.EMAIL_HOST,
                    'port': settings.EMAIL_PORT,
                    'user': settings.EMAIL_HOST_USER,
                    'from_email': settings.DEFAULT_FROM_EMAIL,
                    'use_tls': settings.EMAIL_USE_TLS,
                    'use_ssl': settings.EMAIL_USE_SSL,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Email test failed: {str(e)}',
                'email_settings': {
                    'host': getattr(settings, 'EMAIL_HOST', 'Not configured'),
                    'port': getattr(settings, 'EMAIL_PORT', 'Not configured'),
                    'user': getattr(settings, 'EMAIL_HOST_USER', 'Not configured'),
                    'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not configured'),
                }
            }, status=500)


# Function-based view for easier URL routing
def test_email_endpoint(request):
    """Simple function-based email test endpoint"""
    try:
        success = test_email_configuration()
        
        return JsonResponse({
            'status': 'success' if success else 'failed',
            'message': 'Email configuration test completed',
            'timestamp': timezone.now().isoformat(),
            'site_url': settings.SITE_URL,
            'email_from': settings.DEFAULT_FROM_EMAIL,
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Email test failed: {str(e)}',
            'timestamp': timezone.now().isoformat(),
        }, status=500)
