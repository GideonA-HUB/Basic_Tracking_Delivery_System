from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import StaffLoginForm, StaffRegistrationForm, CustomerRegistrationForm, CustomerLoginForm, VIPLoginForm
from .models import StaffProfile, CustomerProfile


def is_staff_user(user):
    """Check if user is a staff member"""
    return user.is_authenticated and user.is_staff


def is_customer_user(user):
    """Check if user is a regular customer"""
    return user.is_authenticated and not user.is_staff


def is_vip_user(user):
    """Check if user is a VIP member"""
    # For now, allow any authenticated user to access VIP
    # In production, you would check for actual VIP status here
    return user.is_authenticated and user.is_active


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
    # Create mock VIP member data for demonstration
    class MockVIPMember:
        def __init__(self, user):
            self.customer = user
            self.member_id = f"VIP-{user.id:06d}"
            self.full_name = user.get_full_name() or user.username
            self.membership_tier = 'gold'
            self.status = 'active'
            self.total_investments = 50000.00
            self.monthly_income = 5000.00
            self.membership_start_date = user.date_joined
            
        def get_membership_tier_display(self):
            return 'Gold VIP'
            
        def get_status_display(self):
            return 'Active'
    
    class MockStaff:
        def __init__(self):
            self.full_name = "Sarah Johnson"
            self.department = "VIP Services"
            self.staff_id = "VIP-STAFF-001"
    
    vip_member = MockVIPMember(request.user)
    assigned_staff = MockStaff()
    
    context = {
        'vip_member': vip_member,
        'assigned_staff': assigned_staff,
        'user': request.user,
    }
    
    return render(request, 'accounts/vip_dashboard.html', context)


@login_required
@user_passes_test(is_vip_user)
def vip_logout(request):
    """VIP logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('frontend:landing_page')
