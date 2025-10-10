from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from .models import VIPMember, VIPStaff, VIPActivity, VIPBenefit, VIPNotification, VIPApplication
from .forms import VIPApplicationForm
from investments.models import UserInvestment, InvestmentPortfolio
import json


@login_required
def vip_dashboard(request):
    """Main VIP dashboard view - only accessible to approved VIP members"""
    try:
        # Check if user has an approved VIP membership
        vip_member = get_object_or_404(VIPMember, customer=request.user, status='active')
        
        # Check if VIP member is approved
        if vip_member.status != 'active':
            messages.error(request, "Your VIP membership is not active. Please contact support.")
            return redirect('vip_members:application_status')
        
        # Get user's investment data
        try:
            portfolio = InvestmentPortfolio.objects.get(user=request.user)
            total_investments = portfolio.total_invested
            current_value = portfolio.current_value
            total_return = portfolio.total_return
            total_return_percentage = portfolio.total_return_percentage
            active_investments_count = portfolio.active_investments_count
        except InvestmentPortfolio.DoesNotExist:
            total_investments = 0
            current_value = 0
            total_return = 0
            total_return_percentage = 0
            active_investments_count = 0
        
        # Get recent activities
        recent_activities = VIPActivity.objects.filter(member=vip_member).order_by('-timestamp')[:5]
        
        # Get unread notifications
        unread_notifications = VIPNotification.objects.filter(
            member=vip_member, 
            is_read=False
        ).order_by('-created_at')[:5]
        
        # Get VIP benefits based on membership tier
        applicable_benefits = VIPBenefit.objects.filter(
            membership_tiers__icontains=vip_member.membership_tier,
            is_active=True
        ).order_by('name')
        
        # Get recent investments
        recent_investments = UserInvestment.objects.filter(
            user=request.user, 
            status='active'
        ).order_by('-purchased_at')[:5]
        
        # Prepare context
        context = {
            'vip_member': vip_member,
            'assigned_staff': vip_member.assigned_staff,
            'total_investments': total_investments,
            'current_value': current_value,
            'total_return': total_return,
            'total_return_percentage': total_return_percentage,
            'active_investments_count': active_investments_count,
            'recent_activities': recent_activities,
            'unread_notifications': unread_notifications,
            'applicable_benefits': applicable_benefits,
            'recent_investments': recent_investments,
            'current_time': timezone.now(),
        }
        
        # Log dashboard access
        VIPActivity.objects.create(
            member=vip_member,
            activity_type='login',
            title='Dashboard Access',
            description=f'Accessed VIP dashboard at {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
        )
        
        return render(request, 'vip_members/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading VIP dashboard: {str(e)}")
        return redirect('vip_members:apply')


@login_required
def vip_profile(request):
    """VIP member profile view"""
    try:
        vip_member = get_object_or_404(VIPMember, customer=request.user)
        
        # Get all activities
        all_activities = VIPActivity.objects.filter(member=vip_member).order_by('-timestamp')
        
        # Get all notifications
        all_notifications = VIPNotification.objects.filter(member=vip_member).order_by('-created_at')
        
        context = {
            'vip_member': vip_member,
            'assigned_staff': vip_member.assigned_staff,
            'all_activities': all_activities,
            'all_notifications': all_notifications,
        }
        
        return render(request, 'vip_members/profile.html', context)
        
    except VIPMember.DoesNotExist:
        messages.error(request, "VIP member profile not found.")
        return redirect('vip_members:dashboard')


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    if request.method == 'POST':
        try:
            notification = get_object_or_404(VIPNotification, id=notification_id, member__customer=request.user)
            notification.is_read = True
            notification.save()
            
            return JsonResponse({'status': 'success', 'message': 'Notification marked as read'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def vip_benefits(request):
    """VIP benefits page"""
    try:
        vip_member = get_object_or_404(VIPMember, customer=request.user)
        
        # Get all benefits for the member's tier
        applicable_benefits = VIPBenefit.objects.filter(
            membership_tiers__icontains=vip_member.membership_tier,
            is_active=True
        ).order_by('name')
        
        # Get benefits for other tiers (for comparison)
        all_benefits = VIPBenefit.objects.filter(is_active=True).order_by('name')
        
        context = {
            'vip_member': vip_member,
            'applicable_benefits': applicable_benefits,
            'all_benefits': all_benefits,
        }
        
        return render(request, 'vip_members/benefits.html', context)
        
    except VIPMember.DoesNotExist:
        messages.error(request, "VIP member profile not found.")
        return redirect('vip_members:dashboard')


@login_required
def vip_support(request):
    """VIP support page"""
    try:
        vip_member = get_object_or_404(VIPMember, customer=request.user)
        
        context = {
            'vip_member': vip_member,
            'assigned_staff': vip_member.assigned_staff,
        }
        
        return render(request, 'vip_members/support.html', context)
        
    except VIPMember.DoesNotExist:
        messages.error(request, "VIP member profile not found.")
        return redirect('vip_members:dashboard')


@login_required
def vip_activities(request):
    """VIP activities history page"""
    try:
        vip_member = get_object_or_404(VIPMember, customer=request.user)
        
        # Get all activities with pagination
        all_activities = VIPActivity.objects.filter(member=vip_member).order_by('-timestamp')
        
        context = {
            'vip_member': vip_member,
            'all_activities': all_activities,
        }
        
        return render(request, 'vip_members/activities.html', context)
        
    except VIPMember.DoesNotExist:
        messages.error(request, "VIP member profile not found.")
        return redirect('vip_members:dashboard')


def vip_membership_info(request):
    """Public VIP membership information page"""
    # Get all VIP benefits
    all_benefits = VIPBenefit.objects.filter(is_active=True).order_by('name')
    
    # Get membership tier information
    tier_info = {
        'bronze': {
            'name': 'Bronze VIP',
            'color': '#CD7F32',
            'description': 'Entry-level VIP membership with basic privileges',
            'min_investment': 10000
        },
        'silver': {
            'name': 'Silver VIP', 
            'color': '#C0C0C0',
            'description': 'Enhanced VIP membership with additional benefits',
            'min_investment': 25000
        },
        'gold': {
            'name': 'Gold VIP',
            'color': '#FFD700', 
            'description': 'Premium VIP membership with exclusive privileges',
            'min_investment': 50000
        },
        'platinum': {
            'name': 'Platinum VIP',
            'color': '#E5E4E2',
            'description': 'Elite VIP membership with premium services',
            'min_investment': 100000
        },
        'diamond': {
            'name': 'Diamond VIP',
            'color': '#B9F2FF',
            'description': 'Ultimate VIP membership with all privileges',
            'min_investment': 250000
        }
    }
    
    context = {
        'all_benefits': all_benefits,
        'tier_info': tier_info,
    }
    
    return render(request, 'vip_members/membership_info.html', context)


@login_required
def vip_application(request):
    """VIP membership application form"""
    try:
        # Check if user already has a VIP membership
        if VIPMember.objects.filter(customer=request.user, status='active').exists():
            messages.info(request, "You already have an active VIP membership!")
            return redirect('vip_members:dashboard')
        
        # Check if user has a pending application
        pending_application = VIPApplication.objects.filter(
            customer=request.user, 
            status__in=['pending', 'under_review', 'requires_info']
        ).first()
        
        if pending_application:
            messages.info(request, "You already have a pending VIP application. Please check your application status.")
            return redirect('vip_members:application_status')
        
        # Check if user has a rejected application
        rejected_application = VIPApplication.objects.filter(
            customer=request.user,
            status='rejected'
        ).first()
        
        if rejected_application:
            messages.warning(request, "Your previous VIP application was rejected. You may apply again.")
        
        if request.method == 'POST':
            form = VIPApplicationForm(request.POST)
            if form.is_valid():
                application = form.save(commit=False)
                application.customer = request.user
                application.save()
                
                messages.success(request, "Your VIP application has been submitted successfully! You will be notified of the decision within 2-3 business days.")
                return redirect('vip_members:application_status')
        else:
            form = VIPApplicationForm()
        
        context = {
            'form': form,
            'has_pending_application': pending_application is not None,
            'has_rejected_application': rejected_application is not None,
            'rejected_application': rejected_application,
        }
        
        return render(request, 'vip_members/application.html', context)
        
    except Exception as e:
        messages.error(request, f"Error processing VIP application: {str(e)}")
        return redirect('tracking:landing_page')


@login_required
def application_status(request):
    """Check VIP application status"""
    try:
        # Get user's VIP application
        application = VIPApplication.objects.filter(customer=request.user).first()
        
        # Get user's VIP membership if approved
        vip_member = VIPMember.objects.filter(customer=request.user, status='active').first()
        
        context = {
            'application': application,
            'vip_member': vip_member,
            'is_vip_member': vip_member is not None,
        }
        
        return render(request, 'vip_members/application_status.html', context)
        
    except Exception as e:
        messages.error(request, f"Error checking application status: {str(e)}")
        return redirect('tracking:landing_page')


def vip_login_redirect(request):
    """Redirect users to appropriate VIP page based on their status"""
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to access VIP features.")
        return redirect('accounts:customer_login')
    
    # Check if user has active VIP membership
    vip_member = VIPMember.objects.filter(customer=request.user, status='active').first()
    if vip_member:
        return redirect('vip_members:dashboard')
    
    # Check if user has pending application
    application = VIPApplication.objects.filter(
        customer=request.user,
        status__in=['pending', 'under_review', 'requires_info']
    ).first()
    if application:
        return redirect('vip_members:application_status')
    
    # Check if user has rejected application
    rejected_application = VIPApplication.objects.filter(
        customer=request.user,
        status='rejected'
    ).first()
    if rejected_application:
        messages.warning(request, "Your previous VIP application was rejected. You may apply again.")
    
    # Redirect to application form
    return redirect('vip_members:apply')
