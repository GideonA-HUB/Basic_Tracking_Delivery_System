from rest_framework import serializers
from .models import Delivery, DeliveryStatus


class DeliveryStatusSerializer(serializers.ModelSerializer):
    """Serializer for delivery status updates"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    formatted_timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliveryStatus
        fields = [
            'id', 'status', 'status_display', 'location', 'description',
            'timestamp', 'formatted_timestamp'
        ]
        read_only_fields = ['timestamp']
    
    def get_formatted_timestamp(self, obj):
        """Format timestamp for display"""
        return obj.timestamp.strftime('%B %d, %Y at %I:%M %p')


class DeliverySerializer(serializers.ModelSerializer):
    """Serializer for delivery entries"""
    
    status_updates = DeliveryStatusSerializer(many=True, read_only=True)
    current_status_display = serializers.CharField(source='get_current_status_display', read_only=True)
    tracking_url = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    formatted_created_at = serializers.SerializerMethodField()
    formatted_estimated_delivery = serializers.SerializerMethodField()
    formatted_actual_delivery = serializers.SerializerMethodField()
    
    class Meta:
        model = Delivery
        fields = [
            'id', 'order_number', 'tracking_number', 'customer_name',
            'customer_email', 'customer_phone', 'pickup_address',
            'delivery_address', 'package_description', 'package_weight',
            'package_dimensions', 'current_status', 'current_status_display',
            'estimated_delivery', 'actual_delivery', 'tracking_url',
            'is_expired', 'status_updates', 'formatted_created_at',
            'formatted_estimated_delivery', 'formatted_actual_delivery',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'tracking_number', 'tracking_secret', 'tracking_link_expires',
            'current_status', 'created_at', 'updated_at'
        ]
    
    def get_tracking_url(self, obj):
        """Get the tracking URL for the delivery"""
        request = self.context.get('request')
        if request:
            # Generate tracking URL using the current request's scheme and host
            scheme = request.scheme
            host = request.get_host()
            
            # Handle port forwarding - use the forwarded host if available
            if 'HTTP_X_FORWARDED_HOST' in request.META:
                host = request.META['HTTP_X_FORWARDED_HOST']
            elif 'HTTP_HOST' in request.META:
                host = request.META['HTTP_HOST']
            
            # Build the tracking URL
            tracking_path = obj.get_tracking_url()
            return f"{scheme}://{host}{tracking_path}"
        return obj.get_tracking_url()
    
    def get_is_expired(self, obj):
        """Check if the tracking link has expired"""
        return obj.is_tracking_link_expired()
    
    def get_formatted_created_at(self, obj):
        """Format created_at for display"""
        return obj.created_at.strftime('%B %d, %Y at %I:%M %p')
    
    def get_formatted_estimated_delivery(self, obj):
        """Format estimated_delivery for display"""
        if obj.estimated_delivery:
            return obj.estimated_delivery.strftime('%B %d, %Y at %I:%M %p')
        return None
    
    def get_formatted_actual_delivery(self, obj):
        """Format actual_delivery for display"""
        if obj.actual_delivery:
            return obj.actual_delivery.strftime('%B %d, %Y at %I:%M %p')
        return None


class DeliveryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating delivery entries"""
    
    tracking_number = serializers.CharField(read_only=True)
    tracking_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Delivery
        fields = [
            'order_number', 'customer_name', 'customer_email', 'customer_phone',
            'pickup_address', 'delivery_address', 'package_description',
            'package_weight', 'package_dimensions', 'estimated_delivery',
            'tracking_number', 'tracking_url'
        ]
    
    def get_tracking_url(self, obj):
        """Get the tracking URL for the delivery"""
        request = self.context.get('request')
        if request:
            # Generate tracking URL using the current request's scheme and host
            scheme = request.scheme
            host = request.get_host()
            
            # Handle port forwarding - use the forwarded host if available
            if 'HTTP_X_FORWARDED_HOST' in request.META:
                host = request.META['HTTP_X_FORWARDED_HOST']
            elif 'HTTP_HOST' in request.META:
                host = request.META['HTTP_HOST']
            
            # Build the tracking URL
            tracking_path = obj.get_tracking_url()
            return f"{scheme}://{host}{tracking_path}"
        return obj.get_tracking_url()
    
    def create(self, validated_data):
        """Create a new delivery with tracking information"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        
        delivery = Delivery.objects.create(**validated_data)
        
        # Create initial status update
        DeliveryStatus.objects.create(
            delivery=delivery,
            status='pending',
            description='Order received and pending confirmation'
        )
        
        return delivery


class DeliveryStatusCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating delivery status updates"""
    
    class Meta:
        model = DeliveryStatus
        fields = ['status', 'location', 'description']
    
    def validate_delivery(self, value):
        """Validate that the delivery exists and is not expired"""
        if value.is_tracking_link_expired():
            raise serializers.ValidationError("This delivery tracking link has expired.")
        return value


class TrackingResponseSerializer(serializers.ModelSerializer):
    """Serializer for tracking response (public API)"""
    
    status_updates = DeliveryStatusSerializer(many=True, read_only=True)
    current_status_display = serializers.CharField(source='get_current_status_display', read_only=True)
    formatted_created_at = serializers.SerializerMethodField()
    formatted_estimated_delivery = serializers.SerializerMethodField()
    formatted_actual_delivery = serializers.SerializerMethodField()
    
    class Meta:
        model = Delivery
        fields = [
            'order_number', 'tracking_number', 'customer_name',
            'pickup_address', 'delivery_address', 'package_description',
            'current_status', 'current_status_display', 'estimated_delivery',
            'actual_delivery', 'status_updates', 'formatted_created_at',
            'formatted_estimated_delivery', 'formatted_actual_delivery'
        ]
    
    def get_formatted_created_at(self, obj):
        """Format created_at for display"""
        return obj.created_at.strftime('%B %d, %Y at %I:%M %p')
    
    def get_formatted_estimated_delivery(self, obj):
        """Format estimated_delivery for display"""
        if obj.estimated_delivery:
            return obj.estimated_delivery.strftime('%B %d, %Y at %I:%M %p')
        return None
    
    def get_formatted_actual_delivery(self, obj):
        """Format actual_delivery for display"""
        if obj.actual_delivery:
            return obj.actual_delivery.strftime('%B %d, %Y at %I:%M %p')
        return None
