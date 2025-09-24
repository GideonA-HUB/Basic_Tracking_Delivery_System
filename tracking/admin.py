from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Delivery, DeliveryStatus, DeliveryCheckpoint, NewsletterSubscriber
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


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'first_name', 'last_name', 'is_active', 'source', 'subscribed_at', 'admin_actions'
    ]
    list_filter = ['is_active', 'source', 'subscribed_at', 'unsubscribed_at']
    search_fields = ['email', 'first_name', 'last_name', 'ip_address']
    readonly_fields = ['subscribed_at', 'unsubscribed_at']
    list_per_page = 50
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'first_name', 'last_name', 'is_active')
        }),
        ('Subscription Details', {
            'fields': ('source', 'subscribed_at', 'unsubscribed_at')
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent', 'preferences'),
            'classes': ('collapse',)
        }),
    )
    
    def admin_actions(self, obj):
        """Display action buttons"""
        if obj.is_active:
            return format_html(
                '<a href="{}" class="button" style="background: #EF4444; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Unsubscribe</a>',
                reverse('admin:tracking_newslettersubscriber_unsubscribe', args=[obj.pk])
            )
        else:
            return format_html(
                '<a href="{}" class="button" style="background: #10B981; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Resubscribe</a>',
                reverse('admin:tracking_newslettersubscriber_resubscribe', args=[obj.pk])
            )
    admin_actions.short_description = 'Actions'
    
    def get_urls(self):
        """Add custom admin URLs"""
        urls = super().get_urls()
        custom_urls = [
            path('unsubscribe/<int:subscriber_id>/', self.admin_site.admin_view(self.unsubscribe_view), name='tracking_newslettersubscriber_unsubscribe'),
            path('resubscribe/<int:subscriber_id>/', self.admin_site.admin_view(self.resubscribe_view), name='tracking_newslettersubscriber_resubscribe'),
            path('export-subscribers/', self.admin_site.admin_view(self.export_subscribers_view), name='tracking_newslettersubscriber_export'),
        ]
        return custom_urls + urls
    
    def unsubscribe_view(self, request, subscriber_id):
        """Unsubscribe a subscriber"""
        try:
            subscriber = NewsletterSubscriber.objects.get(id=subscriber_id)
            subscriber.unsubscribe()
            messages.success(request, f'{subscriber.email} has been unsubscribed successfully.')
        except NewsletterSubscriber.DoesNotExist:
            messages.error(request, 'Subscriber not found.')
        return redirect('admin:tracking_newslettersubscriber_changelist')
    
    def resubscribe_view(self, request, subscriber_id):
        """Resubscribe a subscriber"""
        try:
            subscriber = NewsletterSubscriber.objects.get(id=subscriber_id)
            subscriber.resubscribe()
            messages.success(request, f'{subscriber.email} has been resubscribed successfully.')
        except NewsletterSubscriber.DoesNotExist:
            messages.error(request, 'Subscriber not found.')
        return redirect('admin:tracking_newslettersubscriber_changelist')
    
    def export_subscribers_view(self, request):
        """Export subscribers to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter_subscribers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'First Name', 'Last Name', 'Status', 'Source', 'Subscribed At'])
        
        subscribers = NewsletterSubscriber.objects.all().order_by('-subscribed_at')
        for subscriber in subscribers:
            writer.writerow([
                subscriber.email,
                subscriber.first_name or '',
                subscriber.last_name or '',
                'Active' if subscriber.is_active else 'Inactive',
                subscriber.source,
                subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response