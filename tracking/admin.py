from django.contrib import admin
from .models import Delivery, DeliveryStatus


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'tracking_number', 'order_number', 'customer_name', 
        'current_status', 'created_at', 'tracking_link_expires'
    ]
    list_filter = ['current_status', 'created_at', 'tracking_link_expires']
    search_fields = ['tracking_number', 'order_number', 'customer_name', 'customer_email']
    readonly_fields = ['tracking_number', 'tracking_secret', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('order_number', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Address Information', {
            'fields': ('pickup_address', 'delivery_address')
        }),
        ('Package Information', {
            'fields': ('package_description', 'package_weight', 'package_dimensions')
        }),
        ('Tracking Information', {
            'fields': ('tracking_number', 'tracking_secret', 'tracking_link_expires')
        }),
        ('Status Information', {
            'fields': ('current_status', 'estimated_delivery', 'actual_delivery')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = [
        'delivery', 'status', 'location', 'timestamp'
    ]
    list_filter = ['status', 'timestamp']
    search_fields = ['delivery__tracking_number', 'delivery__customer_name', 'description']
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('delivery')
