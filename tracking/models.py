from django.db import models
from django.utils import timezone
from django.conf import settings
import secrets
import string


class Delivery(models.Model):
    """Model for delivery entries"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('returned', 'Returned'),
    ]
    
    # Basic delivery information
    order_number = models.CharField(max_length=100, unique=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Address information
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    
    # Package information
    package_description = models.TextField()
    package_weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    package_dimensions = models.CharField(max_length=100, blank=True, null=True)
    
    # Tracking information
    tracking_number = models.CharField(max_length=100, unique=True)
    tracking_secret = models.CharField(max_length=100, unique=True)
    tracking_link_expires = models.DateTimeField()
    
    # Status and timestamps
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_delivery = models.DateTimeField(blank=True, null=True)
    actual_delivery = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries_created'
    )
    
    class Meta:
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery {self.tracking_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        if not self.tracking_secret:
            self.tracking_secret = self.generate_tracking_secret()
        if not self.tracking_link_expires:
            from django.utils import timezone
            from django.conf import settings
            self.tracking_link_expires = timezone.now() + timezone.timedelta(
                days=getattr(settings, 'TRACKING_LINK_EXPIRY_DAYS', 30)
            )
        super().save(*args, **kwargs)
    
    def generate_tracking_number(self):
        """Generate a unique tracking number"""
        import random
        import string
        
        while True:
            # Generate a 12-character alphanumeric tracking number
            tracking_number = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=12)
            )
            if not Delivery.objects.filter(tracking_number=tracking_number).exists():
                return tracking_number
    
    def generate_tracking_secret(self):
        """Generate a secure tracking secret"""
        secret_length = getattr(settings, 'TRACKING_LINK_SECRET_LENGTH', 32)
        return secrets.token_urlsafe(secret_length)
    
    def is_tracking_link_expired(self):
        """Check if the tracking link has expired"""
        return timezone.now() > self.tracking_link_expires
    
    def get_tracking_url(self):
        """Generate the tracking URL"""
        from django.urls import reverse
        return reverse('frontend:track_delivery', kwargs={
            'tracking_number': self.tracking_number,
            'tracking_secret': self.tracking_secret
        })


class DeliveryStatus(models.Model):
    """Model for delivery status updates"""
    
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='status_updates'
    )
    status = models.CharField(max_length=20, choices=Delivery.STATUS_CHOICES)
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.delivery.tracking_number} - {self.status} at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        # Update the delivery's current status
        self.delivery.current_status = self.status
        self.delivery.save()
        super().save(*args, **kwargs)
