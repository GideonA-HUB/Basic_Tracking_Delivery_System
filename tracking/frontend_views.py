from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Delivery


def is_staff_user(user):
    """Check if user is a staff member"""
    return user.is_authenticated and user.is_staff


def tracking_page(request, tracking_number, tracking_secret):
    """Frontend tracking page"""
    try:
        delivery = Delivery.objects.get(
            tracking_number=tracking_number,
            tracking_secret=tracking_secret
        )
        
        # Check if tracking link has expired
        if delivery.is_tracking_link_expired():
            return render(request, 'tracking/expired.html', {
                'delivery': delivery,
                'expired_at': delivery.tracking_link_expires
            })
        
        return render(request, 'tracking/tracking_page.html', {
            'delivery': delivery,
            'tracking_number': tracking_number,
            'tracking_secret': tracking_secret
        })
        
    except Delivery.DoesNotExist:
        raise Http404("Delivery not found")


@login_required
@user_passes_test(is_staff_user)
def dashboard(request):
    """Admin dashboard for managing deliveries"""
    deliveries = Delivery.objects.all().order_by('-created_at')[:50]
    
    # Get statistics
    total_deliveries = Delivery.objects.count()
    pending_deliveries = Delivery.objects.filter(current_status='pending').count()
    in_transit_deliveries = Delivery.objects.filter(current_status='in_transit').count()
    delivered_deliveries = Delivery.objects.filter(current_status='delivered').count()
    
    context = {
        'deliveries': deliveries,
        'total_deliveries': total_deliveries,
        'pending_deliveries': pending_deliveries,
        'in_transit_deliveries': in_transit_deliveries,
        'delivered_deliveries': delivered_deliveries,
    }
    
    return render(request, 'tracking/dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
def create_delivery_page(request):
    """Page for creating new deliveries"""
    return render(request, 'tracking/create_delivery.html')


def where_is_my_parcel(request):
    """Page for Where's My Parcel? support"""
    return render(request, 'tracking/where_is_my_parcel.html')


def tracking_status_guide(request):
    """Page for Understanding Tracking Status"""
    return render(request, 'tracking/tracking_status_guide.html')


def calculate_cost(request):
    """Page for Calculate Time and Cost"""
    return render(request, 'tracking/calculate_cost.html')


def landing_page(request):
    """Public landing page for customers"""
    return render(request, 'tracking/landing_page.html')
