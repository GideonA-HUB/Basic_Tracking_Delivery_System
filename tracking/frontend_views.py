from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Delivery
import json


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


@csrf_exempt
@require_http_methods(["POST"])
def search_tracking_number(request):
    """Handle tracking number searches from landing page"""
    try:
        data = json.loads(request.body)
        tracking_number = data.get('tracking_number', '').strip()
        
        if not tracking_number:
            return JsonResponse({
                'error': 'Please provide a tracking number'
            }, status=400)
        
        # Try to find the delivery
        try:
            delivery = Delivery.objects.get(tracking_number=tracking_number)
            
            # Check if tracking link has expired
            if delivery.is_tracking_link_expired():
                return JsonResponse({
                    'error': 'This tracking link has expired',
                    'expired_at': delivery.tracking_link_expires.isoformat()
                }, status=410)
            
            # Generate tracking URL using the current request's scheme and host
            scheme = request.scheme
            host = request.get_host()
            
            # Handle port forwarding - use the forwarded host if available
            if 'HTTP_X_FORWARDED_HOST' in request.META:
                host = request.META['HTTP_X_FORWARDED_HOST']
            elif 'HTTP_HOST' in request.META:
                host = request.META['HTTP_HOST']
            
            # Build the tracking URL
            tracking_path = delivery.get_tracking_url()
            tracking_url = f"{scheme}://{host}{tracking_path}"
            
            return JsonResponse({
                'success': True,
                'tracking_url': tracking_url,
                'tracking_number': delivery.tracking_number
            })
            
        except Delivery.DoesNotExist:
            return JsonResponse({
                'error': 'Tracking number not found. Please check your tracking number and try again.'
            }, status=404)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid request data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'An error occurred while processing your request'
        }, status=500)


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
