from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from .forms import StaffLoginForm, StaffRegistrationForm, CustomerRegistrationForm, CustomerLoginForm, VIPLoginForm, CardApplicationForm, LocalTransferForm, InternationalTransferForm, WireTransferForm, CryptocurrencyForm, PayPalForm, WiseTransferForm, CashAppForm, SkrillForm, VenmoForm, ZelleForm, RevolutForm, AlipayForm, WeChatPayForm, DepositForm, LoanApplicationForm, IRSTaxRefundForm, KYCVerificationForm, KYCTermsForm
from .models import StaffProfile, CustomerProfile, VIPProfile, Transaction, Card, LocalTransfer, InternationalTransfer, Deposit, Loan, LoanApplication, LoanFAQ, IRSTaxRefund, LoanHistory, AccountSettings, SupportTicket, VIPFinancialMetrics, KYCVerification


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
        
        # Get or create financial metrics for this VIP member
        financial_metrics, created = VIPFinancialMetrics.objects.get_or_create(
            vip_member=vip_profile,
            defaults={
                'current_balance': 0.00,
                'monthly_income': 0.00,
                'monthly_outgoing': 0.00,
                'total_investments': 0.00,
                'net_worth': 100000.00,
                'transaction_limit': 500000.00,
                'pending_transactions': 0.00,
                'transaction_volume': 0.00,
            }
        )
        
        # Get recent activities for this VIP member
        recent_activities = vip_profile.recent_activities.filter(
            is_active=True
        ).order_by('-display_order', '-activity_date')[:10]  # Show last 10 activities
        
        # Get recent transactions for statistics
        recent_transactions = vip_profile.transactions.filter(
            is_active=True
        ).order_by('-transaction_date')[:5]
        
        # Get account statistics
        total_transactions = vip_profile.transactions.filter(is_active=True).count()
        pending_transactions = vip_profile.transactions.filter(
            is_active=True, status='pending'
        ).count()
        
        context = {
            'vip_member': vip_profile,
            'assigned_staff': assigned_staff,
            'user': request.user,
            'recent_activities': recent_activities,
            'recent_transactions': recent_transactions,
            'financial_metrics': financial_metrics,
            'total_transactions': total_transactions,
            'pending_transactions': pending_transactions,
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
        
        # Get cards for this VIP member
        cards = vip_profile.cards.filter(is_active=True)
        
        # Calculate statistics
        active_cards = cards.filter(status='active').count()
        pending_applications = cards.filter(status='pending').count()
        total_balance = sum(card.current_balance for card in cards.filter(status='active'))
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'cards': cards,
            'active_cards_count': active_cards,
            'pending_applications_count': pending_applications,
            'total_balance': total_balance,
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
        
        if request.method == 'POST':
            form = LocalTransferForm(request.POST)
            if form.is_valid():
                # Create the transfer
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                
                # Calculate transfer fee (example: 1% of amount, minimum $5, maximum $50)
                amount = transfer.transfer_amount
                fee_percentage = 0.01  # 1%
                calculated_fee = amount * fee_percentage
                transfer.transfer_fee = max(5.00, min(calculated_fee, 50.00))
                
                transfer.save()
                
                messages.success(request, f'Transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = LocalTransferForm()
        
        # Get recent transfers for this VIP member
        recent_transfers = vip_profile.local_transfers.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'recent_transfers': recent_transfers,
        }
        
        return render(request, 'accounts/vip_transfer_local.html', context)
        
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
        
        if request.method == 'POST':
            form = DepositForm(request.POST)
            deposit_method = request.POST.get('deposit_method')
            
            if form.is_valid() and deposit_method:
                # Create the deposit
                deposit = form.save(commit=False)
                deposit.vip_member = vip_profile
                deposit.deposit_method = deposit_method
                deposit.status = 'pending'
                
                # Update VIP member's balance (in a real app, this would be done after payment confirmation)
                # For now, we'll just save the deposit request
                deposit.save()
                
                messages.success(request, f'Deposit request submitted successfully! Reference: {deposit.reference_number}')
                return redirect('accounts:vip_dashboard')
            else:
                if not deposit_method:
                    messages.error(request, 'Please select a deposit method.')
                messages.error(request, 'Please correct the errors below.')
        else:
            form = DepositForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
        }
        
        return render(request, 'accounts/vip_deposit.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_card_application(request):
    """VIP card application page"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = CardApplicationForm(request.POST)
            if form.is_valid():
                # Create the card application
                card = form.save(commit=False)
                card.vip_member = vip_profile
                card.card_name = form.cleaned_data['cardholder_name']
                card.application_fee = card.get_application_fee
                
                # Generate a temporary card number (masked)
                import random
                last_four = str(random.randint(1000, 9999))
                card.card_number = f"**** **** **** {last_four}"
                
                # Set expiry date (2 years from now)
                from datetime import datetime, timedelta
                expiry_date = datetime.now() + timedelta(days=730)
                card.expiry_month = str(expiry_date.month).zfill(2)
                card.expiry_year = str(expiry_date.year)
                
                card.save()
                
                messages.success(request, 'Card Application now available now')
                return redirect('accounts:vip_cards')
        else:
            form = CardApplicationForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
        }
        
        return render(request, 'accounts/vip_card_application.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_international(request):
    """VIP international transfer page"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = InternationalTransferForm(request.POST)
            if form.is_valid():
                # Create the transfer
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                
                # Calculate transfer fee based on method (example rates)
                amount = transfer.transfer_amount
                method = transfer.transfer_method
                
                # Different fee structures for different methods
                if method == 'wire_transfer':
                    transfer.transfer_fee = max(25.00, amount * 0.005)  # $25 minimum or 0.5%
                elif method == 'cryptocurrency':
                    transfer.transfer_fee = amount * 0.02  # 2%
                elif method in ['paypal', 'wise_transfer']:
                    transfer.transfer_fee = amount * 0.03  # 3%
                elif method in ['cash_app', 'venmo', 'zelle']:
                    transfer.transfer_fee = amount * 0.015  # 1.5%
                else:
                    transfer.transfer_fee = amount * 0.025  # 2.5% default
                
                # Cap fees at $100
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)
                
                transfer.save()
                
                messages.success(request, f'International transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = InternationalTransferForm()
        
        # Get recent international transfers for this VIP member
        recent_transfers = vip_profile.international_transfers.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'recent_transfers': recent_transfers,
        }
        
        return render(request, 'accounts/vip_transfer_international.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


# Individual transfer method views
@login_required
@user_passes_test(is_vip_user)
def vip_transfer_wire(request):
    """VIP Wire Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = WireTransferForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'wire_transfer'
                
                # Calculate fees for wire transfer
                amount = transfer.transfer_amount
                transfer.transfer_fee = max(25.00, amount * 0.005)  # $25 minimum or 0.5%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'Wire transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = WireTransferForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'Wire Transfer',
            'processing_time': 'Funds will reflect in the Beneficiary Account within 72hours.',
            'icon_class': 'fas fa-university',
            'icon_color': 'bg-green-500',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_cryptocurrency(request):
    """VIP Cryptocurrency Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = CryptocurrencyForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'cryptocurrency'
                
                # Calculate fees for cryptocurrency
                amount = transfer.transfer_amount
                transfer.transfer_fee = amount * 0.02  # 2%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'Cryptocurrency transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = CryptocurrencyForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'Cryptocurrency Withdrawal',
            'processing_time': 'Withdrawals are typically processed within 1-3 hours.',
            'icon_class': 'fab fa-bitcoin',
            'icon_color': 'bg-orange-500',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_paypal(request):
    """VIP PayPal Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = PayPalForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'paypal'
                
                # Calculate fees for PayPal
                amount = transfer.transfer_amount
                transfer.transfer_fee = amount * 0.03  # 3%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'PayPal transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = PayPalForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'PayPal Withdrawal',
            'processing_time': 'Funds will be sent to your PayPal account within 24 hours.',
            'icon_class': 'fab fa-paypal',
            'icon_color': 'bg-blue-600',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_wise(request):
    """VIP Wise Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = WiseTransferForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'wise_transfer'
                
                # Calculate fees for Wise
                amount = transfer.transfer_amount
                transfer.transfer_fee = amount * 0.03  # 3%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'Wise transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = WiseTransferForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'Wise Transfer Withdrawal',
            'processing_time': 'Your funds will be processed within 1-2 business days.',
            'icon_class': 'fas fa-exchange-alt',
            'icon_color': 'bg-teal-500',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_cashapp(request):
    """VIP Cash App Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = CashAppForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'cash_app'
                
                # Calculate fees for Cash App
                amount = transfer.transfer_amount
                transfer.transfer_fee = amount * 0.015  # 1.5%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'Cash App transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = CashAppForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'Cash App Withdrawal',
            'processing_time': 'Withdrawals to Cash App are typically processed within 24 hours.',
            'icon_class': 'fas fa-dollar-sign',
            'icon_color': 'bg-pink-500',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_skrill(request):
    """VIP Skrill Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = SkrillForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'skrill'
                
                # Calculate fees for Skrill
                amount = transfer.transfer_amount
                transfer.transfer_fee = amount * 0.025  # 2.5%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'Skrill transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = SkrillForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'Skrill Withdrawal',
            'processing_time': 'Withdrawals to Skrill are processed within 24 hours.',
            'icon_class': 'fas fa-credit-card',
            'icon_color': 'bg-purple-500',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_venmo(request):
    """VIP Venmo Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = VenmoForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'venmo'
                
                # Calculate fees for Venmo
                amount = transfer.transfer_amount
                transfer.transfer_fee = amount * 0.015  # 1.5%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'Venmo transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = VenmoForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'Venmo Withdrawal',
            'processing_time': 'Funds will be transferred to your Venmo account within 24 hours.',
            'icon_class': 'fab fa-cc-visa',
            'icon_color': 'bg-blue-500',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_zelle(request):
    """VIP Zelle Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = ZelleForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'zelle'
                
                # Calculate fees for Zelle
                amount = transfer.transfer_amount
                transfer.transfer_fee = amount * 0.015  # 1.5%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'Zelle transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = ZelleForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'Zelle Withdrawal',
            'processing_time': 'Funds will be sent to your Zelle account typically within a few hours.',
            'icon_class': 'fas fa-mobile-alt',
            'icon_color': 'bg-purple-600',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_revolut(request):
    """VIP Revolut Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = RevolutForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'revolut'
                
                # Calculate fees for Revolut
                amount = transfer.transfer_amount
                transfer.transfer_fee = amount * 0.025  # 2.5%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'Revolut transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = RevolutForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'Revolut Withdrawal',
            'processing_time': 'Funds will be transferred to your Revolut account within 1-2 business days.',
            'icon_class': 'fas fa-globe',
            'icon_color': 'bg-cyan-500',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_alipay(request):
    """VIP Alipay Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = AlipayForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'alipay'
                
                # Calculate fees for Alipay
                amount = transfer.transfer_amount
                transfer.transfer_fee = amount * 0.025  # 2.5%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'Alipay transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = AlipayForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'Alipay Withdrawal',
            'processing_time': 'Withdrawals to Alipay are typically processed within 24-48 hours.',
            'icon_class': 'fas fa-qrcode',
            'icon_color': 'bg-blue-800',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_transfer_wechat(request):
    """VIP WeChat Pay Transfer form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = WeChatPayForm(request.POST)
            if form.is_valid():
                transfer = form.save(commit=False)
                transfer.vip_member = vip_profile
                transfer.transfer_method = 'wechat_pay'
                
                # Calculate fees for WeChat Pay
                amount = transfer.transfer_amount
                transfer.transfer_fee = amount * 0.025  # 2.5%
                transfer.transfer_fee = min(transfer.transfer_fee, 100.00)  # Cap at $100
                
                transfer.save()
                
                messages.success(request, f'WeChat Pay transfer request submitted successfully! Reference: {transfer.reference_number}')
                return redirect('accounts:vip_dashboard')
        else:
            form = WeChatPayForm()
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
            'transfer_method': 'WeChat Pay Withdrawal',
            'processing_time': 'Funds will be sent to your WeChat Pay account within 24-48 hours.',
            'icon_class': 'fab fa-weixin',
            'icon_color': 'bg-green-600',
        }
        
        return render(request, 'accounts/vip_transfer_method.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_loan_services(request):
    """VIP loan services information page"""
    try:
        vip_profile = request.user.vip_profile
        
        # Get all active loans
        loans = Loan.objects.filter(is_active=True)
        
        # Get FAQs
        faqs = LoanFAQ.objects.filter(is_active=True)[:2]  # Show first 2 on main page
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'loans': loans,
            'faqs': faqs,
        }
        
        return render(request, 'accounts/vip_loan_services.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_loan_application(request):
    """VIP loan application form"""
    try:
        vip_profile = request.user.vip_profile
        
        if request.method == 'POST':
            form = LoanApplicationForm(request.POST)
            if form.is_valid():
                # Create the loan application
                application = form.save(commit=False)
                application.vip_member = vip_profile
                application.status = 'pending'
                
                # Set default values from VIP profile if not provided
                if not application.phone_number and vip_profile.phone:
                    application.phone_number = vip_profile.phone
                
                application.save()
                
                messages.success(request, f'Loan application submitted successfully! Reference: {application.reference_number}')
                return redirect('accounts:vip_loan_services')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = LoanApplicationForm()
            # Pre-populate with VIP profile data if available
            if vip_profile.phone:
                form.fields['phone_number'].initial = vip_profile.phone
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'form': form,
        }
        
        return render(request, 'accounts/vip_loan_application.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def vip_loan_faqs(request):
    """VIP loan FAQs page"""
    try:
        vip_profile = request.user.vip_profile
        
        # Get all active FAQs
        faqs = LoanFAQ.objects.filter(is_active=True)
        
        context = {
            'vip_member': vip_profile,
            'user': request.user,
            'faqs': faqs,
        }
        
        return render(request, 'accounts/vip_loan_faqs.html', context)
    
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('accounts:vip_dashboard')


@login_required
def vip_irs_tax_refund(request):
    """IRS Tax Refund request page"""
    if not hasattr(request.user, 'vip_profile'):
        messages.error(request, 'Access denied. VIP membership required.')
        return redirect('accounts:vip_dashboard')
    
    vip_profile = request.user.vip_profile
    
    if request.method == 'POST':
        form = IRSTaxRefundForm(request.POST)
        if form.is_valid():
            refund_request = form.save(commit=False)
            refund_request.vip_member = vip_profile
            refund_request.save()
            
            messages.success(request, f'Your IRS Tax Refund request has been submitted successfully! Reference Number: {refund_request.reference_number}')
            return redirect('accounts:vip_irs_tax_refund_status')
    else:
        form = IRSTaxRefundForm()
    
    context = {
        'vip_profile': vip_profile,
        'form': form,
    }
    
    return render(request, 'accounts/vip_irs_tax_refund.html', context)


@login_required
def vip_irs_tax_refund_status(request):
    """IRS Tax Refund status page"""
    if not hasattr(request.user, 'vip_profile'):
        messages.error(request, 'Access denied. VIP membership required.')
        return redirect('accounts:vip_dashboard')
    
    vip_profile = request.user.vip_profile
    refund_requests = IRSTaxRefund.objects.filter(vip_member=vip_profile).order_by('-created_at')
    
    context = {
        'vip_profile': vip_profile,
        'refund_requests': refund_requests,
    }
    
    return render(request, 'accounts/vip_irs_tax_refund_status.html', context)


@login_required
def vip_loan_history(request):
    """Loan History page"""
    if not hasattr(request.user, 'vip_profile'):
        messages.error(request, 'Access denied. VIP membership required.')
        return redirect('accounts:vip_dashboard')
    
    vip_profile = request.user.vip_profile
    
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Get loan history for this VIP member
    loan_history = LoanHistory.objects.filter(vip_member=vip_profile)
    
    # Apply search filter if provided
    if search_query:
        loan_history = loan_history.filter(
            Q(purpose__icontains=search_query) | 
            Q(amount__icontains=search_query) |
            Q(loan_type__icontains=search_query) |
            Q(reference_number__icontains=search_query)
        )
    
    # Order by date applied (newest first)
    loan_history = loan_history.order_by('-date_applied')
    
    context = {
        'vip_profile': vip_profile,
        'loan_history': loan_history,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/vip_loan_history.html', context)


@login_required
def vip_account_settings(request):
    """Account Settings page"""
    if not hasattr(request.user, 'vip_profile'):
        messages.error(request, 'Access denied. VIP membership required.')
        return redirect('accounts:vip_dashboard')
    
    vip_profile = request.user.vip_profile
    
    # Get or create account settings
    account_settings, created = AccountSettings.objects.get_or_create(
        vip_member=vip_profile,
        defaults={
            'first_name': vip_profile.full_name.split()[0] if vip_profile.full_name else "",
            'last_name': " ".join(vip_profile.full_name.split()[1:]) if vip_profile.full_name and len(vip_profile.full_name.split()) > 1 else "",
            'email': request.user.email if request.user.email else "",
        }
    )
    
    if request.method == 'POST':
        # Handle form submission
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        phone_number = request.POST.get('phone_number', '')
        date_of_birth = request.POST.get('date_of_birth', '')
        address = request.POST.get('address', '')
        
        # Update account settings
        account_settings.first_name = first_name
        account_settings.last_name = last_name
        account_settings.email = email
        account_settings.phone_number = phone_number
        
        if date_of_birth:
            try:
                from datetime import datetime
                account_settings.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        account_settings.address = address
        account_settings.save()
        
        messages.success(request, 'Your account settings have been updated successfully!')
        return redirect('accounts:vip_account_settings')
    
    context = {
        'vip_profile': vip_profile,
        'account_settings': account_settings,
    }
    
    return render(request, 'accounts/vip_account_settings.html', context)


@login_required
def vip_support_ticket(request):
    """Support Ticket submission page"""
    if not hasattr(request.user, 'vip_profile'):
        messages.error(request, 'Access denied. VIP membership required.')
        return redirect('accounts:vip_dashboard')
    
    vip_profile = request.user.vip_profile
    
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'low')
        category = request.POST.get('category', 'general')
        
        # Validate required fields
        if not title:
            messages.error(request, 'Please provide a ticket title.')
        elif not description:
            messages.error(request, 'Please provide a description of your issue.')
        else:
            # Create support ticket
            try:
                ticket = SupportTicket.objects.create(
                    vip_member=vip_profile,
                    title=title,
                    description=description,
                    priority=priority,
                    category=category,
                    status='open'
                )
                messages.success(request, f'Support ticket {ticket.ticket_number} has been created successfully! Our team will respond within 24 hours.')
                return redirect('accounts:vip_support_ticket')
            except Exception as e:
                messages.error(request, 'An error occurred while creating your ticket. Please try again.')
    
    # Get recent tickets for this user
    recent_tickets = SupportTicket.objects.filter(vip_member=vip_profile)[:5]
    
    context = {
        'vip_profile': vip_profile,
        'recent_tickets': recent_tickets,
    }
    
    return render(request, 'accounts/vip_support_ticket.html', context)


@login_required
@user_passes_test(is_vip_user)
def kyc_welcome(request):
    """KYC Welcome page with terms and conditions"""
    try:
        vip_profile = request.user.vip_profile
        
        # Check if KYC already exists
        kyc_verification, created = KYCVerification.objects.get_or_create(
            vip_member=vip_profile,
            defaults={'status': 'pending'}
        )
        
        # If KYC is already approved, redirect to dashboard
        if kyc_verification.is_approved:
            messages.info(request, 'Your KYC verification is already approved.')
            return redirect('accounts:vip_dashboard')
        
        context = {
            'vip_member': vip_profile,
            'kyc_verification': kyc_verification,
        }
        
        return render(request, 'accounts/kyc_welcome.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def kyc_verification(request):
    """KYC verification form page"""
    try:
        vip_profile = request.user.vip_profile
        
        # Get or create KYC verification
        kyc_verification, created = KYCVerification.objects.get_or_create(
            vip_member=vip_profile,
            defaults={
                'full_name': vip_profile.full_name,
                'email': vip_profile.user.email,
                'status': 'pending'
            }
        )
        
        # If KYC is already approved, redirect to dashboard
        if kyc_verification.is_approved:
            messages.info(request, 'Your KYC verification is already approved.')
            return redirect('accounts:vip_dashboard')
        
        # If KYC is not approved and terms not accepted, redirect to welcome
        if not kyc_verification.terms_accepted:
            return redirect('accounts:kyc_welcome')
        
        if request.method == 'POST':
            form = KYCVerificationForm(request.POST, request.FILES, instance=kyc_verification)
            if form.is_valid():
                kyc_verification = form.save(commit=False)
                kyc_verification.status = 'pending'
                kyc_verification.save()
                
                messages.success(request, 'KYC verification submitted successfully. We will review your information and get back to you soon.')
                return redirect('accounts:vip_dashboard')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = KYCVerificationForm(instance=kyc_verification)
        
        context = {
            'vip_member': vip_profile,
            'kyc_verification': kyc_verification,
            'form': form,
        }
        
        return render(request, 'accounts/kyc_verification.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')


@login_required
@user_passes_test(is_vip_user)
def kyc_terms_accept(request):
    """Accept KYC terms and conditions"""
    if request.method == 'POST':
        try:
            vip_profile = request.user.vip_profile
            kyc_verification = KYCVerification.objects.get(vip_member=vip_profile)
            
            # Mark terms as accepted
            kyc_verification.terms_accepted = True
            kyc_verification.terms_accepted_at = timezone.now()
            kyc_verification.save()
            
            messages.success(request, 'Terms and conditions accepted. You can now proceed with KYC verification.')
            return redirect('accounts:kyc_verification')
            
        except VIPProfile.DoesNotExist:
            messages.error(request, 'VIP profile not found. Please contact support.')
            return redirect('frontend:landing_page')
        except KYCVerification.DoesNotExist:
            messages.error(request, 'KYC verification not found. Please start the process again.')
            return redirect('accounts:kyc_welcome')
    
    return redirect('accounts:kyc_welcome')


@login_required
@user_passes_test(is_vip_user)
def kyc_status(request):
    """KYC verification status page"""
    try:
        vip_profile = request.user.vip_profile
        
        try:
            kyc_verification = KYCVerification.objects.get(vip_member=vip_profile)
        except KYCVerification.DoesNotExist:
            messages.info(request, 'You have not started the KYC verification process yet.')
            return redirect('accounts:kyc_welcome')
        
        context = {
            'vip_member': vip_profile,
            'kyc_verification': kyc_verification,
        }
        
        return render(request, 'accounts/kyc_status.html', context)
        
    except VIPProfile.DoesNotExist:
        messages.error(request, 'VIP profile not found. Please contact support.')
        return redirect('frontend:landing_page')
