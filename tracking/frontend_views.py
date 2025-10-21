from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Delivery, NewsletterSubscriber
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
            'tracking_secret': tracking_secret,
            'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
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


def landing_page_figma(request):
    """Figma redesigned landing page"""
    return render(request, 'tracking/landing_page_figma.html')


@csrf_exempt
@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email address is required'
            }, status=400)
        
        # Check if email is already subscribed
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'This email is already subscribed to our newsletter'
            }, status=400)
        
        # Get client information
        ip_address = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create new subscriber
        subscriber = NewsletterSubscriber.objects.create(
            email=email,
            source='website',
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Successfully subscribed to newsletter'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while subscribing. Please try again.'
        }, status=500)


def faqs(request):
    """FAQ page with comprehensive questions and answers"""
    faq_data = {
        'general': [
            {
                'question': 'What is Meridian Asset Logistics?',
                'answer': 'Meridian Asset Logistics is a comprehensive logistics and investment platform that combines cutting-edge supply chain solutions with strategic investment opportunities. We provide end-to-end logistics services including maritime, air freight, ground transportation, and warehousing, while also offering investment opportunities in logistics assets.'
            },
            {
                'question': 'How do I get started with Meridian Asset Logistics?',
                'answer': 'Getting started is easy! You can create an account on our website, explore our investment marketplace, or contact our team for personalized logistics solutions. For VIP members, we offer exclusive access to premium services and investment opportunities.'
            },
            {
                'question': 'What services does Meridian Asset Logistics offer?',
                'answer': 'We offer comprehensive logistics services including maritime shipping, air freight, ground transportation, warehousing, customs brokerage, and supply chain management. Additionally, we provide investment opportunities in logistics assets and portfolio management services.'
            },
            {
                'question': 'How can I contact customer support?',
                'answer': 'You can reach our customer support team 24/7 through multiple channels: email at support@meridianassetlogistics.com, phone at +1 (555) 123-4567, or through our online support center. VIP members have access to dedicated account managers.'
            }
        ],
        'investment': [
            {
                'question': 'What investment opportunities are available?',
                'answer': 'We offer diverse investment opportunities including logistics asset investments, portfolio management, real-time trading, and strategic partnerships. Our investment marketplace features various asset categories with different risk profiles and return potentials.'
            },
            {
                'question': 'How do I become a VIP member?',
                'answer': 'VIP membership is available through our application process. VIP members enjoy exclusive benefits including priority support, dedicated account managers, premium investment opportunities, faster processing times, and enhanced transaction limits.'
            },
            {
                'question': 'What are the minimum investment requirements?',
                'answer': 'Investment requirements vary by opportunity and membership level. Standard investments start from $1,000, while VIP members have access to exclusive opportunities with different minimum thresholds. Contact our investment team for personalized guidance.'
            },
            {
                'question': 'How secure are my investments?',
                'answer': 'Security is our top priority. We use advanced encryption, multi-factor authentication, and comply with international financial regulations. All investments are backed by real logistics assets and managed by certified professionals.'
            }
        ],
        'logistics': [
            {
                'question': 'How do I track my shipments?',
                'answer': 'You can track your shipments using our online tracking system by entering your tracking number. We provide real-time updates on shipment status, location, and estimated delivery times. VIP members receive priority tracking and detailed analytics.'
            },
            {
                'question': 'What shipping methods are available?',
                'answer': 'We offer comprehensive shipping solutions including maritime, air freight, ground transportation, and express delivery. Our services cover domestic and international shipping with various speed and cost options to meet your needs.'
            },
            {
                'question': 'How do I calculate shipping costs?',
                'answer': 'You can use our online cost calculator to get instant quotes based on package dimensions, weight, destination, and service level. Our system provides transparent pricing with no hidden fees.'
            },
            {
                'question': 'What is your delivery guarantee?',
                'answer': 'We provide delivery guarantees based on service level selected. Express services include time-definite delivery guarantees, while standard services have estimated delivery windows. VIP members receive enhanced guarantees and priority handling.'
            }
        ],
        'vip': [
            {
                'question': 'What are VIP member benefits?',
                'answer': 'VIP members enjoy exclusive benefits including dedicated account managers, priority support, premium investment opportunities, enhanced transaction limits, faster processing times, exclusive events, and personalized logistics solutions.'
            },
            {
                'question': 'How do I apply for VIP membership?',
                'answer': 'VIP membership applications are available through our website. The process includes completing a comprehensive application, providing required documentation, and meeting eligibility criteria. Our team reviews applications and provides personalized guidance.'
            },
            {
                'question': 'What is the VIP membership fee?',
                'answer': 'VIP membership includes various fee structures depending on the membership tier and services selected. Contact our VIP team for detailed information about membership fees and benefits tailored to your needs.'
            },
            {
                'question': 'Do VIP members get priority support?',
                'answer': 'Yes! VIP members receive 24/7 priority support with dedicated account managers, faster response times, and access to exclusive support channels. Our VIP support team is specially trained to handle complex logistics and investment needs.'
            }
        ],
        'technical': [
            {
                'question': 'How do I reset my password?',
                'answer': 'You can reset your password by clicking "Forgot Password" on the login page. Enter your email address and follow the instructions sent to your email. For VIP members, contact your dedicated account manager for assistance.'
            },
            {
                'question': 'Is my data secure?',
                'answer': 'Absolutely. We use industry-standard encryption, secure servers, and comply with international data protection regulations. All personal and financial information is protected with advanced security measures and regular security audits.'
            },
            {
                'question': 'Can I access my account from mobile devices?',
                'answer': 'Yes! Our platform is fully responsive and optimized for mobile devices. You can access all features including tracking, investments, and account management from any smartphone or tablet.'
            },
            {
                'question': 'What browsers are supported?',
                'answer': 'Our platform supports all modern browsers including Chrome, Firefox, Safari, and Edge. We recommend using the latest version of your preferred browser for the best experience.'
            }
        ]
    }
    
    return render(request, 'tracking/faqs.html', {
        'faq_data': faq_data,
        'page_title': 'Frequently Asked Questions'
    })


def claims(request):
    """Claims information and submission page"""
    return render(request, 'tracking/claims.html', {
        'page_title': 'Claims - File a Claim'
    })


def support_center(request):
    """Support center with help resources and contact options"""
    return render(request, 'tracking/support_center.html', {
        'page_title': 'Support Center - Get Help'
    })


def logistics(request):
    """Logistics services information page"""
    return render(request, 'tracking/logistics.html', {
        'page_title': 'Logistics Services'
    })


def warehousing(request):
    """Warehousing services information page"""
    return render(request, 'tracking/warehousing.html', {
        'page_title': 'Warehousing Solutions'
    })


def distribution(request):
    """Distribution services information page"""
    return render(request, 'tracking/distribution.html', {
        'page_title': 'Distribution Services'
    })


def customs_brokerage(request):
    """Customs brokerage services information page"""
    return render(request, 'tracking/customs_brokerage.html', {
        'page_title': 'Customs Brokerage Services'
    })