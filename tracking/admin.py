from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Delivery, DeliveryStatus, DeliveryCheckpoint
import json


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'tracking_number', 'order_number', 'customer_name', 
        'current_status', 'has_geolocation', 'gps_status', 'courier_name', 'created_at', 'live_tracking_actions'
    ]
    list_filter = ['current_status', 'gps_tracking_enabled', 'created_at', 'tracking_link_expires']
    search_fields = ['tracking_number', 'order_number', 'customer_name', 'customer_email', 'courier_name']
    readonly_fields = ['tracking_number', 'tracking_secret', 'created_at', 'updated_at', 'last_location_update', 'last_gps_update']
    fieldsets = (
        ('Basic Information', {
            'fields': ('order_number', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Address Information', {
            'fields': ('pickup_address', 'delivery_address')
        }),
        ('Courier Information', {
            'fields': ('courier_name', 'courier_phone', 'courier_vehicle_type', 'courier_vehicle_number'),
            'classes': ('collapse',)
        }),
        ('Geolocation Information', {
            'fields': (
                ('pickup_latitude', 'pickup_longitude'),
                ('delivery_latitude', 'delivery_longitude'),
                ('current_latitude', 'current_longitude'),
                'current_location_name',
                'last_location_update',
                'last_gps_update'
            ),
            'classes': ('collapse',)
        }),
        ('GPS Tracking Settings', {
            'fields': ('gps_tracking_enabled', 'location_update_frequency'),
            'classes': ('collapse',)
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
    
    def has_geolocation(self, obj):
        """Display if delivery has geolocation data"""
        if obj.has_geolocation():
            return format_html('<span style="color: green;">✓ GPS Active</span>')
        return format_html('<span style="color: red;">✗ No GPS</span>')
    has_geolocation.short_description = 'GPS Status'
    
    def gps_status(self, obj):
        """Display GPS tracking status"""
        if obj.is_gps_active():
            return format_html('<span style="color: green;">🟢 Live GPS</span>')
        elif obj.gps_tracking_enabled:
            return format_html('<span style="color: orange;">🟡 GPS Enabled</span>')
        else:
            return format_html('<span style="color: red;">🔴 GPS Off</span>')
    gps_status.short_description = 'GPS Tracking'
    
    def live_tracking_actions(self, obj):
        """Display live tracking action buttons"""
        if obj.has_geolocation():
            return format_html(
                '<a href="{}" class="button" style="background: #3B82F6; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">View Live Map</a> '
                '<a href="{}" class="button" style="background: #10B981; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Update Location</a>',
                reverse('admin:tracking_delivery_live_map', args=[obj.pk]),
                reverse('admin:tracking_delivery_update_location', args=[obj.pk])
            )
        return format_html(
            '<a href="{}" class="button" style="background: #EF4444; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Add GPS</a>',
            reverse('admin:tracking_delivery_update_location', args=[obj.pk])
        )
    live_tracking_actions.short_description = 'Live Tracking'
    
    def get_urls(self):
        """Add custom admin URLs"""
        urls = super().get_urls()
        custom_urls = [
            path('live-map/<int:delivery_id>/', self.admin_site.admin_view(self.live_map_view), name='tracking_delivery_live_map'),
            path('update-location/<int:delivery_id>/', self.admin_site.admin_view(self.update_location_view), name='tracking_delivery_update_location'),
            path('global-dashboard/', self.admin_site.admin_view(self.global_dashboard_view), name='tracking_global_dashboard'),
            path('add-checkpoint/<int:delivery_id>/', self.admin_site.admin_view(self.add_checkpoint_view), name='tracking_delivery_add_checkpoint'),
        ]
        return custom_urls + urls
    
    def live_map_view(self, request, delivery_id):
        """Live map view for specific delivery"""
        try:
            delivery = Delivery.objects.get(id=delivery_id)
        except Delivery.DoesNotExist:
            messages.error(request, 'Delivery not found')
            return redirect('admin:tracking_delivery_changelist')
        
        context = {
            'title': f'Live Map - {delivery.tracking_number}',
            'delivery': delivery,
            'has_permission': True,
            'opts': self.model._meta,
        }
        return render(request, 'admin/tracking/delivery/live_map.html', context)
    
    def update_location_view(self, request, delivery_id):
        """Update location view"""
        try:
            delivery = Delivery.objects.get(id=delivery_id)
        except Delivery.DoesNotExist:
            messages.error(request, 'Delivery not found')
            return redirect('admin:tracking_delivery_changelist')
        
        if request.method == 'POST':
            try:
                latitude = float(request.POST.get('latitude'))
                longitude = float(request.POST.get('longitude'))
                location_name = request.POST.get('location_name', '')
                accuracy = request.POST.get('accuracy')
                
                if accuracy:
                    accuracy = float(accuracy)
                
                delivery.update_current_location(
                    latitude=latitude,
                    longitude=longitude,
                    location_name=location_name,
                    accuracy=accuracy
                )
                
                # If this is an AJAX request, return JSON
                if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and 'application/json' in request.headers.get('Accept', ''):
                    return JsonResponse({'success': True, 'message': 'Location updated successfully'})
                
                messages.success(request, f'Location updated successfully for {delivery.tracking_number}')
                return redirect('admin:tracking_delivery_change', delivery_id)
                
            except (ValueError, TypeError) as e:
                if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded' and 'application/json' in request.headers.get('Accept', ''):
                    return JsonResponse({'success': False, 'error': f'Invalid location data: {e}'})
                messages.error(request, f'Invalid location data: {e}')
        
        context = {
            'title': f'Update Location - {delivery.tracking_number}',
            'delivery': delivery,
            'has_permission': True,
            'opts': self.model._meta,
        }
        return render(request, 'admin/tracking/delivery/update_location.html', context)
    
    def global_dashboard_view(self, request):
        """Global dashboard view for all active deliveries"""
        active_deliveries = Delivery.objects.filter(
            current_status__in=['confirmed', 'in_transit', 'out_for_delivery']
        ).select_related('created_by')
        
        context = {
            'title': 'Global Delivery Dashboard',
            'deliveries': active_deliveries,
            'has_permission': True,
            'opts': self.model._meta,
        }
        return render(request, 'admin/tracking/delivery/global_dashboard.html', context)
    
    def add_checkpoint_view(self, request, delivery_id):
        """Add checkpoint view"""
        try:
            delivery = Delivery.objects.get(id=delivery_id)
        except Delivery.DoesNotExist:
            messages.error(request, 'Delivery not found')
            return redirect('admin:tracking_delivery_changelist')
        
        if request.method == 'POST':
            try:
                checkpoint_type = request.POST.get('checkpoint_type')
                location_name = request.POST.get('location_name')
                latitude = float(request.POST.get('latitude'))
                longitude = float(request.POST.get('longitude'))
                description = request.POST.get('description', '')
                courier_notes = request.POST.get('courier_notes', '')
                
                DeliveryCheckpoint.objects.create(
                    delivery=delivery,
                    checkpoint_type=checkpoint_type,
                    location_name=location_name,
                    latitude=latitude,
                    longitude=longitude,
                    description=description,
                    courier_notes=courier_notes
                )
                
                messages.success(request, f'Checkpoint added successfully for {delivery.tracking_number}')
                return redirect('admin:tracking_delivery_change', delivery_id)
                
            except (ValueError, TypeError) as e:
                messages.error(request, f'Invalid checkpoint data: {e}')
        
        context = {
            'title': f'Add Checkpoint - {delivery.tracking_number}',
            'delivery': delivery,
            'has_permission': True,
            'opts': self.model._meta,
        }
        return render(request, 'admin/tracking/delivery/add_checkpoint.html', context)


@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = [
        'delivery', 'status', 'location', 'has_geolocation', 'timestamp'
    ]
    list_filter = ['status', 'timestamp']
    search_fields = ['delivery__tracking_number', 'delivery__customer_name', 'description']
    readonly_fields = ['timestamp']
    fieldsets = (
        ('Status Information', {
            'fields': ('delivery', 'status', 'location', 'description')
        }),
        ('Geolocation Information', {
            'fields': (
                ('latitude', 'longitude'),
                'location_name',
                'accuracy'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def has_geolocation(self, obj):
        """Display if status update has geolocation data"""
        if obj.latitude and obj.longitude:
            return format_html('<span style="color: green;">✓ GPS</span>')
        return format_html('<span style="color: red;">✗ No GPS</span>')
    has_geolocation.short_description = 'GPS'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('delivery')


@admin.register(DeliveryCheckpoint)
class DeliveryCheckpointAdmin(admin.ModelAdmin):
    list_display = [
        'delivery', 'checkpoint_type', 'location_name', 'has_geolocation', 'timestamp', 'customer_notified'
    ]
    list_filter = ['checkpoint_type', 'timestamp', 'customer_notified']
    search_fields = ['delivery__tracking_number', 'delivery__customer_name', 'location_name', 'description']
    readonly_fields = ['timestamp']
    fieldsets = (
        ('Checkpoint Information', {
            'fields': ('delivery', 'checkpoint_type', 'location_name', 'description')
        }),
        ('Geolocation Information', {
            'fields': (
                ('latitude', 'longitude'),
                'accuracy'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'estimated_arrival', 'actual_arrival'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('courier_notes', 'customer_notified'),
            'classes': ('collapse',)
        }),
    )
    
    def has_geolocation(self, obj):
        """Display if checkpoint has geolocation data"""
        if obj.latitude and obj.longitude:
            return format_html('<span style="color: green;">✓ GPS</span>')
        return format_html('<span style="color: red;">✗ No GPS</span>')
    has_geolocation.short_description = 'GPS'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('delivery')
