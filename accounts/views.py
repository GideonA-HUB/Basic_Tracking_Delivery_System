from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .forms import StaffLoginForm, StaffRegistrationForm, CustomerRegistrationForm, CustomerLoginForm, VIPLoginForm
from .models import StaffProfile, CustomerProfile, VIPProfile, Transaction


def is_staff_user(user):
    """Check if user is a staff member"""
    return user.is_authenticated and user.is_staff


def is_customer_user(user):
    """Check if user is a regular customer"""
    return user.is_authenticated and not user.is_staff


def is_vip_user(user):
    """Check if user is a VIP member"""
    try:
        return user.is_authenticated and hasattr(user, 'vip_profile') and user.vip_profile.status == 'active'
    except VIPProfile.DoesNotExist:
        return False


def customer_register(request):
    """Customer registration view"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('frontend:dashboard')
        else:
            return redirect('frontend:landing_page')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, f'Welcome to Meridian Asset Logistics, {user.get_full_name()}! Your account has been created successfully.')
                return redirect('frontend:landing_page')
            except Exception as e:
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error creating customer account: {str(e)}")
                messages.error(request, 'An error occurred while creating your account. Please try again or contact support.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'accounts/customer_register.html', {'form': form})


def customer_login(request):
    """Customer login view"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('frontend:dashboard')
        else:
            return redirect('frontend:landing_page')
    
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate with username first, then email
            user = authenticate(username=username, password=password)
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is not None and not user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('frontend:landing_page')
            else:
                messages.error(request, 'Invalid credentials or access denied.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerLoginForm()
    
    return render(request, 'accounts/customer_login.html', {'form': form})


def customer_logout(request):
    """Customer logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('frontend:landing_page')


def staff_login(request):
    """Staff login view"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('frontend:dashboard')
    
    if request.method == 'POST':
        form = StaffLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('frontend:dashboard')
            else:
                messages.error(request, 'Invalid credentials or access denied.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StaffLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
@user_passes_test(is_staff_user)
def staff_logout(request):
    """Staff logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:login')


@user_passes_test(lambda u: u.is_superuser)
def staff_registration(request):
    """Staff registration view (admin only)"""
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Staff member {user.get_full_name()} has been created successfully.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@user_passes_test(is_staff_user)
def staff_profile(request):
    """Staff profile view"""
    try:
        profile = request.user.staff_profile
    except StaffProfile.DoesNotExist:
        profile = None
    
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
@user_passes_test(is_customer_user)
def customer_profile(request):
    """Customer profile view"""
    try:
        profile = request.user.customer_profile
    except CustomerProfile.DoesNotExist:
        profile = None
    
    return render(request, 'accounts/customer_profile.html', {'profile': profile})


def vip_login(request):
    """VIP login view"""
    if request.user.is_authenticated and is_vip_user(request.user):
        return redirect('accounts:vip_dashboard')
    
    if request.method == 'POST':
        form = VIPLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate with username first, then email
            user = authenticate(username=username, password=password)
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is not None and is_vip_user(user):
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('accounts:vip_dashboard')
            else:
                messages.error(request, 'Invalid VIP credentials or access denied.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VIPLoginForm()
    
    return render(request, 'accounts/vip_login.html', {'form': form})


@login_required
@user_passes_test(is_vip_user)
def vip_dashboard(request):
    """VIP dashboard view - Silver Bridge Bank style"""
    try:
        vip_profile = request.user.vip_profile
        assigned_staff = vip_profile.assigned_staff
        
        # Get recent activities for this VIP member
        recent_activities = vip_profile.recent_activities.filter(
            is_active=True
        ).order_by('-display_order', '-activity_date')[:10]  # Show last 10 activities
        
        context = {
            'vip_member': vip_profile,
            'assigned_staff': assigned_staff,
            'user': request.user,
            'recent_activities': recent_activities,
        }
        
        return render(request, 'accounts/vip_dashboard.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_logout(request):
    """VIP logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transactions(request):
    """VIP transactions page"""
    try:
        vip_profile = request.user.vip_profile
        
        # Get search and filter parameters
        search_query = request.GET.get('search', '')
        transaction_type = request.GET.get('type', '')
        status = request.GET.get('status', '')
        scope = request.GET.get('scope', '')
        
        # Base queryset
        transactions = vip_profile.transactions.filter(is_active=True)
        
        # Apply filters
        if search_query:
            transactions = transactions.filter(
                Q(reference_id__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(notes__icontains=search_query)
            )
        
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        
        if status:
            transactions = transactions.filter(status=status)
        
        if scope:
            transactions = transactions.filter(scope=scope)
        
        # Pagination
        paginator = Paginator(transactions, 20)  # 20 transactions per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get filter options for dropdowns
        transaction_types = Transaction.TRANSACTION_TYPE_CHOICES
        status_choices = Transaction.STATUS_CHOICES
        scope_choices = Transaction.SCOPE_CHOICES
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'transactions': page_obj,
            'search_query': search_query,
            'selected_type': transaction_type,
            'selected_status': status,
            'selected_scope': scope,
            'transaction_types': transaction_types,
            'status_choices': status_choices,
            'scope_choices': scope_choices,
            'total_transactions': transactions.count(),
        }
        
        return render(request, 'accounts/vip_transactions.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_cards(request):
    """VIP cards page"""
    try:
        vip_profile = request.user.vip_profile
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
        }
        
        return render(request, 'accounts/vip_cards.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_local(request):
    """VIP local transfer page"""
    try:
        vip_profile = request.user.vip_profile
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'transfer_type': 'local',
        }
        
        return render(request, 'accounts/vip_transfer.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_international(request):
    """VIP international transfer page"""
    try:
        vip_profile = request.user.vip_profile
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'transfer_type': 'international',
        }
        
        return render(request, 'accounts/vip_transfer.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_deposit(request):
    """VIP deposit page"""
    try:
        vip_profile = request.user.vip_profile
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
        }
        
        return render(request, 'accounts/vip_deposit.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')
