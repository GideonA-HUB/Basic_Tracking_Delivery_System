from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomerProfile(models.Model):
    """Extended profile for regular customers/users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_active_customer = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Customer"


class StaffProfile(models.Model):
    """Extended profile for staff members"""
    
    ROLE_CHOICES = [
        ('customer_care', 'Customer Care Representative'),
        ('manager', 'Manager'),
        ('admin', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer_care')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    is_active_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staff Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    @property
    def is_customer_care(self):
        return self.role == 'customer_care'
    
    @property
    def is_manager_or_admin(self):
        return self.role in ['manager', 'admin']


class VIPProfile(models.Model):
    """VIP member profile with enhanced features"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Approval'),
        ('suspended', 'Suspended'),
    ]
    
    MEMBERSHIP_TIER_CHOICES = [
        ('bronze', 'Bronze VIP'),
        ('silver', 'Silver VIP'),
        ('gold', 'Gold VIP'),
        ('platinum', 'Platinum VIP'),
        ('diamond', 'Diamond VIP'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vip_profile')
    member_id = models.CharField(max_length=20, unique=True, help_text="Unique VIP member identifier")
    
    # Staff assignment
    assigned_staff = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='assigned_vip_members', help_text="VIP Staff member assigned to this customer")
    
    # Membership details
    membership_tier = models.CharField(max_length=20, choices=MEMBERSHIP_TIER_CHOICES, default='bronze')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Personal information
    phone = models.CharField(max_length=20, blank=True, null=True)
    preferred_contact_method = models.CharField(max_length=20, 
                                              choices=[('email', 'Email'), ('phone', 'Phone'), ('both', 'Both')],
                                              default='email')
    
    # VIP Benefits
    priority_support = models.BooleanField(default=True)
    dedicated_account_manager = models.BooleanField(default=True)
    exclusive_investment_opportunities = models.BooleanField(default=True)
    faster_processing = models.BooleanField(default=True)
    
    # Financial information
    total_investments = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    net_worth = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Timestamps
    membership_start_date = models.DateTimeField(auto_now_add=True)
    last_contact_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes and comments
    notes = models.TextField(blank=True, null=True, help_text="Internal notes about the VIP member")
    
    class Meta:
        verbose_name = 'VIP Profile'
        verbose_name_plural = 'VIP Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_membership_tier_display()}"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def staff_name(self):
        return self.assigned_staff.user.get_full_name() if self.assigned_staff else "Not Assigned"
    
    @property
    def membership_duration_days(self):
        from django.utils import timezone
        return (timezone.now() - self.membership_start_date).days
    
    def save(self, *args, **kwargs):
        """Auto-generate member_id if not provided"""
        if not self.member_id:
            import uuid
            self.member_id = f"VIP-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """Create customer profile when user is created (if not staff)"""
    if created and not instance.is_staff:
        CustomerProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    """Save customer profile when user is saved"""
    if hasattr(instance, 'customer_profile'):
        instance.customer_profile.save()


@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    """Create staff profile when user is created"""
    if created and instance.is_staff:
        StaffProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_staff_profile(sender, instance, **kwargs):
    """Save staff profile when user is saved"""
    if hasattr(instance, 'staff_profile'):
        instance.staff_profile.save()


class RecentActivity(models.Model):
    """Recent activity entries for VIP dashboard"""
    
    ACTIVITY_TYPE_CHOICES = [
        ('investment_return', 'Investment Return'),
        ('wire_transfer', 'International Wire Transfer'),
        ('dividend_payment', 'Dividend Payment'),
        ('service_fee', 'Service Fee'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('loan_payment', 'Loan Payment'),
        ('interest_payment', 'Interest Payment'),
        ('refund', 'Refund'),
        ('commission', 'Commission'),
        ('bonus', 'Bonus'),
        ('penalty', 'Penalty'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('processing', 'Processing'),
    ]
    
    TRANSACTION_DIRECTION_CHOICES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]
    
    # VIP member this activity belongs to
    vip_member = models.ForeignKey(VIPProfile, on_delete=models.CASCADE, related_name='recent_activities')
    
    # Activity details
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES, default='other')
    title = models.CharField(max_length=200, help_text="Display title for the activity")
    description = models.TextField(blank=True, null=True, help_text="Detailed description of the activity")
    
    # Transaction details
    amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Transaction amount (positive for incoming, negative for outgoing)")
    currency = models.CharField(max_length=3, default='USD', help_text="Currency code (USD, EUR, etc.)")
    direction = models.CharField(max_length=10, choices=TRANSACTION_DIRECTION_CHOICES, 
                                help_text="Whether this is an incoming or outgoing transaction")
    
    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    activity_date = models.DateTimeField(help_text="When this activity occurred")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional information
    reference_number = models.CharField(max_length=100, blank=True, null=True, 
                                      help_text="Transaction reference number")
    notes = models.TextField(blank=True, null=True, help_text="Internal notes about this activity")
    
    # Display order
    display_order = models.PositiveIntegerField(default=0, help_text="Order for displaying activities (higher numbers first)")
    
    # Admin fields
    is_active = models.BooleanField(default=True, help_text="Whether this activity should be displayed")
    is_featured = models.BooleanField(default=False, help_text="Whether this activity should be highlighted")
    
    class Meta:
        verbose_name = 'Recent Activity'
        verbose_name_plural = 'Recent Activities'
        ordering = ['-display_order', '-activity_date', '-created_at']
        indexes = [
            models.Index(fields=['vip_member', '-activity_date']),
            models.Index(fields=['status', '-activity_date']),
            models.Index(fields=['is_active', '-activity_date']),
        ]
    
    def __str__(self):
        return f"{self.vip_member.user.username} - {self.title} ({self.amount} {self.currency})"
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency and direction"""
        if self.amount >= 0:
            return f"+${self.amount:,.2f}"
        else:
            return f"-${abs(self.amount):,.2f}"
    
    @property
    def amount_color_class(self):
        """Return CSS class for amount color based on direction"""
        if self.direction == 'incoming' or self.amount >= 0:
            return 'text-green-600'
        else:
            return 'text-red-600'
    
    @property
    def icon_class(self):
        """Return FontAwesome icon class based on activity type"""
        icon_map = {
            'investment_return': 'fas fa-chart-line',
            'wire_transfer': 'fas fa-exchange-alt',
            'dividend_payment': 'fas fa-coins',
            'service_fee': 'fas fa-receipt',
            'deposit': 'fas fa-plus-circle',
            'withdrawal': 'fas fa-minus-circle',
            'loan_payment': 'fas fa-hand-holding-usd',
            'interest_payment': 'fas fa-percentage',
            'refund': 'fas fa-undo',
            'commission': 'fas fa-percentage',
            'bonus': 'fas fa-gift',
            'penalty': 'fas fa-exclamation-triangle',
            'other': 'fas fa-file-alt',
        }
        return icon_map.get(self.activity_type, 'fas fa-file-alt')
    
    @property
    def icon_color_class(self):
        """Return CSS class for icon color based on direction"""
        if self.direction == 'incoming' or self.amount >= 0:
            return 'text-green-600 bg-green-100'
        else:
            return 'text-red-600 bg-red-100'
    
    @property
    def status_color_class(self):
        """Return CSS class for status badge color"""
        status_colors = {
            'completed': 'bg-gray-100 text-gray-800',
            'pending': 'bg-yellow-100 text-yellow-800',
            'failed': 'bg-red-100 text-red-800',
            'cancelled': 'bg-gray-100 text-gray-800',
            'processing': 'bg-blue-100 text-blue-800',
        }
        return status_colors.get(self.status, 'bg-gray-100 text-gray-800')
    
    @property
    def short_date(self):
        """Return short formatted date (e.g., 'Oct 12')"""
        from django.utils import timezone
        if self.activity_date:
            return self.activity_date.strftime('%b %d')
        return ''
    
    def save(self, *args, **kwargs):
        """Auto-set direction based on amount"""
        if self.amount >= 0:
            self.direction = 'incoming'
        else:
            self.direction = 'outgoing'
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """Transaction model for VIP dashboard"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('investment', 'Investment'),
        ('loan', 'Loan'),
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('fee', 'Fee'),
        ('interest', 'Interest'),
        ('dividend', 'Dividend'),
        ('bonus', 'Bonus'),
        ('commission', 'Commission'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('processing', 'Processing'),
        ('reversed', 'Reversed'),
    ]
    
    SCOPE_CHOICES = [
        ('internal', 'Internal'),
        ('external', 'External'),
        ('international', 'International'),
        ('local', 'Local'),
    ]
    
    # VIP member this transaction belongs to
    vip_member = models.ForeignKey(VIPProfile, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Transaction amount")
    currency = models.CharField(max_length=3, default='USD', help_text="Currency code (USD, EUR, etc.)")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, default='other')
    
    # Status and scope
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='internal')
    
    # Identification and description
    reference_id = models.CharField(max_length=100, unique=True, help_text="Unique transaction reference ID")
    description = models.TextField(help_text="Transaction description")
    
    # Dates
    transaction_date = models.DateTimeField(help_text="When the transaction occurred")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True, help_text="Internal notes about this transaction")
    metadata = models.JSONField(blank=True, null=True, help_text="Additional transaction metadata")
    
    # Admin fields
    is_active = models.BooleanField(default=True, help_text="Whether this transaction should be displayed")
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['vip_member', '-transaction_date']),
            models.Index(fields=['status', '-transaction_date']),
            models.Index(fields=['transaction_type', '-transaction_date']),
            models.Index(fields=['reference_id']),
        ]
    
    def __str__(self):
        return f"{self.vip_member.user.username} - {self.reference_id} ({self.amount} {self.currency})"
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency"""
        return f"{self.amount:,.2f} {self.currency}"
    
    @property
    def amount_color_class(self):
        """Return CSS class for amount color based on transaction type"""
        if self.transaction_type in ['deposit', 'refund', 'dividend', 'interest', 'bonus', 'commission']:
            return 'text-green-600'
        elif self.transaction_type in ['withdrawal', 'fee', 'payment']:
            return 'text-red-600'
        else:
            return 'text-gray-600'
    
    @property
    def status_color_class(self):
        """Return CSS class for status badge color"""
        status_colors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'completed': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800',
            'cancelled': 'bg-gray-100 text-gray-800',
            'processing': 'bg-blue-100 text-blue-800',
            'reversed': 'bg-orange-100 text-orange-800',
        }
        return status_colors.get(self.status, 'bg-gray-100 text-gray-800')
    
    @property
    def scope_color_class(self):
        """Return CSS class for scope badge color"""
        scope_colors = {
            'internal': 'bg-blue-100 text-blue-800',
            'external': 'bg-purple-100 text-purple-800',
            'international': 'bg-green-100 text-green-800',
            'local': 'bg-gray-100 text-gray-800',
        }
        return scope_colors.get(self.scope, 'bg-gray-100 text-gray-800')
    
    @property
    def short_date(self):
        """Return short formatted date (e.g., 'Oct 13, 2025')"""
        if self.transaction_date:
            return self.transaction_date.strftime('%b %d, %Y')
        return ''
    
    def save(self, *args, **kwargs):
        """Auto-generate reference_id if not provided"""
        if not self.reference_id:
            import uuid
            self.reference_id = f"TXN-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)


class Card(models.Model):
    """Virtual Card model for VIP dashboard"""
    
    CARD_TYPE_CHOICES = [
        ('virtual', 'Virtual Card'),
        ('physical', 'Physical Card'),
        ('prepaid', 'Prepaid Card'),
        ('debit', 'Debit Card'),
        ('credit', 'Credit Card'),
    ]
    
    CARD_BRAND_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
    ]
    
    CARD_LEVEL_CHOICES = [
        ('standard', 'Standard - $5.00'),
        ('gold', 'Gold - $15.00'),
        ('platinum', 'Platinum - $25.00'),
        ('black', 'Black - $50.00'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    # VIP member this card belongs to
    vip_member = models.ForeignKey(VIPProfile, on_delete=models.CASCADE, related_name='cards')
    
    # Card details
    card_number = models.CharField(max_length=19, help_text="Masked card number (e.g., **** **** **** 1234)")
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default='virtual')
    card_brand = models.CharField(max_length=20, choices=CARD_BRAND_CHOICES, default='visa', help_text="Card brand (Visa, Mastercard, etc.)")
    card_level = models.CharField(max_length=20, choices=CARD_LEVEL_CHOICES, default='standard', help_text="Card level with associated fee")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Card information
    card_name = models.CharField(max_length=100, help_text="Name on the card")
    expiry_month = models.CharField(max_length=2, help_text="Expiry month (01-12)")
    expiry_year = models.CharField(max_length=4, help_text="Expiry year (YYYY)")
    
    # Financial details
    spending_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Monthly spending limit")
    daily_spending_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Daily spending limit")
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Current card balance")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', help_text="Currency code")
    
    # Application details
    cardholder_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name as it will appear on the card")
    billing_address = models.TextField(blank=True, null=True, help_text="Billing address for verification")
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Card issuance fee")
    terms_accepted = models.BooleanField(default=False, help_text="User accepted terms and conditions")
    
    # Dates
    issue_date = models.DateTimeField(auto_now_add=True, help_text="When the card was issued")
    expiry_date = models.DateTimeField(help_text="When the card expires")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional information
    description = models.TextField(blank=True, null=True, help_text="Card description or purpose")
    notes = models.TextField(blank=True, null=True, help_text="Internal notes about this card")
    
    # Admin fields
    is_active = models.BooleanField(default=True, help_text="Whether this card should be displayed")
    
    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vip_member', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['card_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.vip_member.user.username} - {self.card_name} ({self.card_number})"
    
    @property
    def formatted_expiry_date(self):
        """Return formatted expiry date (e.g., '12/25')"""
        return f"{self.expiry_month}/{self.expiry_year}"
    
    @property
    def formatted_balance(self):
        """Return formatted balance with currency"""
        return f"${self.current_balance:,.2f} {self.currency}"
    
    @property
    def formatted_spending_limit(self):
        """Return formatted spending limit with currency"""
        if self.spending_limit:
            return f"${self.spending_limit:,.2f} {self.currency}"
        return "No limit"
    
    @property
    def status_color_class(self):
        """Return CSS class for status badge color"""
        status_colors = {
            'active': 'bg-green-100 text-green-800',
            'inactive': 'bg-gray-100 text-gray-800',
            'pending': 'bg-yellow-100 text-yellow-800',
            'suspended': 'bg-red-100 text-red-800',
            'expired': 'bg-orange-100 text-orange-800',
            'cancelled': 'bg-gray-100 text-gray-800',
        }
        return status_colors.get(self.status, 'bg-gray-100 text-gray-800')
    
    @property
    def card_type_color_class(self):
        """Return CSS class for card type badge color"""
        type_colors = {
            'virtual': 'bg-blue-100 text-blue-800',
            'physical': 'bg-purple-100 text-purple-800',
            'prepaid': 'bg-green-100 text-green-800',
            'debit': 'bg-orange-100 text-orange-800',
            'credit': 'bg-red-100 text-red-800',
        }
        return type_colors.get(self.card_type, 'bg-gray-100 text-gray-800')
    
    @property
    def get_application_fee(self):
        """Return application fee based on card level"""
        fee_map = {
            'standard': 5.00,
            'gold': 15.00,
            'platinum': 25.00,
            'black': 50.00,
        }
        return fee_map.get(self.card_level, 5.00)
    
    def save(self, *args, **kwargs):
        """Auto-set expiry_date based on expiry_month and expiry_year"""
        if self.expiry_month and self.expiry_year:
            from datetime import datetime
            try:
                self.expiry_date = datetime(int(self.expiry_year), int(self.expiry_month), 1)
            except (ValueError, TypeError):
                pass
        super().save(*args, **kwargs)


class LocalTransfer(models.Model):
    """Local Transfer model for VIP dashboard"""
    
    TRANSFER_TYPE_CHOICES = [
        ('online_banking', 'Online Banking'),
        ('joint_account', 'Joint Account'),
        ('checking', 'Checking'),
        ('savings', 'Savings Account'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # VIP member making the transfer
    vip_member = models.ForeignKey(VIPProfile, on_delete=models.CASCADE, related_name='local_transfers')
    
    # Transfer details
    transfer_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Amount to transfer")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', help_text="Currency code")
    
    # Beneficiary details
    beneficiary_name = models.CharField(max_length=100, help_text="Full name of the beneficiary")
    beneficiary_account_number = models.CharField(max_length=50, help_text="Account number of the beneficiary")
    bank_name = models.CharField(max_length=100, help_text="Name of the beneficiary's bank")
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE_CHOICES, default='online_banking', help_text="Type of transfer")
    
    # Additional information
    description = models.TextField(blank=True, null=True, help_text="Transaction description or purpose")
    
    # Transfer status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Unique transfer reference number")
    
    # Fees and charges
    transfer_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Fee charged for the transfer")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Total amount including fees")
    
    # Dates
    transfer_date = models.DateTimeField(auto_now_add=True, help_text="When the transfer was initiated")
    processed_date = models.DateTimeField(blank=True, null=True, help_text="When the transfer was processed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True, help_text="Internal notes about this transfer")
    
    # Admin fields
    is_active = models.BooleanField(default=True, help_text="Whether this transfer should be displayed")
    
    class Meta:
        verbose_name = 'Local Transfer'
        verbose_name_plural = 'Local Transfers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vip_member', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['transfer_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.vip_member.user.username} - {self.formatted_amount} to {self.beneficiary_name}"
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency"""
        return f"${self.transfer_amount:,.2f} {self.currency}"
    
    @property
    def formatted_total_amount(self):
        """Return formatted total amount with currency"""
        return f"${self.total_amount:,.2f} {self.currency}"
    
    @property
    def formatted_fee(self):
        """Return formatted fee with currency"""
        return f"${self.transfer_fee:,.2f} {self.currency}"
    
    @property
    def status_color_class(self):
        """Return CSS class for status badge color"""
        status_colors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'processing': 'bg-blue-100 text-blue-800',
            'completed': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800',
            'cancelled': 'bg-gray-100 text-gray-800',
        }
        return status_colors.get(self.status, 'bg-gray-100 text-gray-800')
    
        def save(self, *args, **kwargs):
            """Auto-generate reference number and calculate total amount"""
            if not self.reference_number:
                import uuid
                self.reference_number = f"LT-{str(uuid.uuid4())[:8].upper()}"
            
            # Calculate total amount (transfer amount + fees)
            self.total_amount = self.transfer_amount + self.transfer_fee
            
            super().save(*args, **kwargs)


class InternationalTransfer(models.Model):
    """International Transfer model for VIP dashboard"""
    
    TRANSFER_METHOD_CHOICES = [
        ('wire_transfer', 'Wire Transfer'),
        ('cryptocurrency', 'Cryptocurrency'),
        ('paypal', 'PayPal'),
        ('wise_transfer', 'Wise Transfer'),
        ('cash_app', 'Cash App'),
        ('skrill', 'Skrill'),
        ('venmo', 'Venmo'),
        ('zelle', 'Zelle'),
        ('revolut', 'Revolut'),
        ('alipay', 'Alipay'),
        ('wechat_pay', 'WeChat Pay'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
        ('CAD', 'CAD - Canadian Dollar'),
        ('AUD', 'AUD - Australian Dollar'),
        ('JPY', 'JPY - Japanese Yen'),
        ('CHF', 'CHF - Swiss Franc'),
        ('CNY', 'CNY - Chinese Yuan'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ]
    
    # VIP member making the transfer
    vip_member = models.ForeignKey(VIPProfile, on_delete=models.CASCADE, related_name='international_transfers')
    
    # Transfer details
    transfer_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Amount to transfer")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', help_text="Currency code")
    transfer_method = models.CharField(max_length=20, choices=TRANSFER_METHOD_CHOICES, help_text="Method of international transfer")
    
    # Recipient details
    recipient_name = models.CharField(max_length=100, help_text="Full name of the recipient")
    recipient_email = models.EmailField(help_text="Email address of the recipient")
    recipient_phone = models.CharField(max_length=20, blank=True, null=True, help_text="Phone number of the recipient")
    
    # Bank details (for wire transfers)
    bank_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name of the recipient's bank")
    bank_address = models.TextField(blank=True, null=True, help_text="Bank address")
    account_number = models.CharField(max_length=50, blank=True, null=True, help_text="Account number")
    routing_number = models.CharField(max_length=20, blank=True, null=True, help_text="Bank routing number")
    swift_code = models.CharField(max_length=11, blank=True, null=True, help_text="SWIFT/BIC code")
    iban = models.CharField(max_length=34, blank=True, null=True, help_text="IBAN (International Bank Account Number)")
    
    # Wallet details (for crypto/other methods)
    wallet_address = models.CharField(max_length=200, blank=True, null=True, help_text="Cryptocurrency wallet address")
    wallet_type = models.CharField(max_length=50, blank=True, null=True, help_text="Type of wallet (Bitcoin, Ethereum, etc.)")
    
    # Transfer information
    purpose_of_transfer = models.CharField(max_length=100, help_text="Purpose of the transfer")
    description = models.TextField(blank=True, null=True, help_text="Additional transfer description")
    
    # Transfer status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Unique transfer reference number")
    tracking_number = models.CharField(max_length=50, blank=True, null=True, help_text="Tracking number for the transfer")
    
    # Fees and charges
    transfer_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Fee charged for the transfer")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, default=1.000000, help_text="Exchange rate applied")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Total amount including fees")
    
    # Dates
    transfer_date = models.DateTimeField(auto_now_add=True, help_text="When the transfer was initiated")
    processed_date = models.DateTimeField(blank=True, null=True, help_text="When the transfer was processed")
    completed_date = models.DateTimeField(blank=True, null=True, help_text="When the transfer was completed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True, help_text="Internal notes about this transfer")
    compliance_notes = models.TextField(blank=True, null=True, help_text="Compliance and regulatory notes")
    
    # Admin fields
    is_active = models.BooleanField(default=True, help_text="Whether this transfer should be displayed")
    requires_approval = models.BooleanField(default=False, help_text="Whether this transfer requires manual approval")
    
    class Meta:
        verbose_name = 'International Transfer'
        verbose_name_plural = 'International Transfers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vip_member', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['transfer_method', '-created_at']),
            models.Index(fields=['currency', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.vip_member.user.username} - {self.formatted_amount} via {self.get_transfer_method_display()}"
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency"""
        return f"{self.currency} {self.transfer_amount:,.2f}"
    
    @property
    def formatted_total_amount(self):
        """Return formatted total amount with currency"""
        return f"{self.currency} {self.total_amount:,.2f}"
    
    @property
    def formatted_fee(self):
        """Return formatted fee with currency"""
        return f"{self.currency} {self.transfer_fee:,.2f}"
    
    @property
    def status_color_class(self):
        """Return CSS class for status badge color"""
        status_colors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'processing': 'bg-blue-100 text-blue-800',
            'completed': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800',
            'cancelled': 'bg-gray-100 text-gray-800',
            'on_hold': 'bg-orange-100 text-orange-800',
        }
        return status_colors.get(self.status, 'bg-gray-100 text-gray-800')
    
    @property
    def transfer_method_icon(self):
        """Return icon class for transfer method"""
        icons = {
            'wire_transfer': 'fas fa-university',
            'cryptocurrency': 'fab fa-bitcoin',
            'paypal': 'fab fa-paypal',
            'wise_transfer': 'fas fa-exchange-alt',
            'cash_app': 'fas fa-dollar-sign',
            'skrill': 'fas fa-credit-card',
            'venmo': 'fab fa-cc-visa',
            'zelle': 'fas fa-mobile-alt',
            'revolut': 'fas fa-globe',
            'alipay': 'fas fa-qrcode',
            'wechat_pay': 'fab fa-weixin',
        }
        return icons.get(self.transfer_method, 'fas fa-exchange-alt')
    
    def save(self, *args, **kwargs):
        """Auto-generate reference number and calculate total amount"""
        if not self.reference_number:
            import uuid
            self.reference_number = f"IT-{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate total amount (transfer amount + fees)
        self.total_amount = self.transfer_amount + self.transfer_fee
        
        super().save(*args, **kwargs)


class Deposit(models.Model):
    """Model for VIP member deposits"""
    
    DEPOSIT_METHOD_CHOICES = [
        ('usdt', 'USDT'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('bitcoin', 'Bitcoin'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    vip_member = models.ForeignKey(VIPProfile, on_delete=models.CASCADE, related_name='deposits')
    deposit_method = models.CharField(max_length=20, choices=DEPOSIT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Transaction details
    reference_number = models.CharField(max_length=50, unique=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True, help_text="Internal notes for admin")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Deposit'
        verbose_name_plural = 'Deposits'
    
    def __str__(self):
        return f"Deposit {self.reference_number} - {self.vip_member.full_name} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate unique reference number
            import uuid
            self.reference_number = f"DEP{str(uuid.uuid4())[:8].upper()}"
        
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return self.vip_member.full_name
    
    @property
    def member_id(self):
        return self.vip_member.member_id


class Loan(models.Model):
    """Model for different types of loans offered"""
    
    LOAN_TYPE_CHOICES = [
        ('personal_home', 'Personal Home Loans'),
        ('automobile', 'Automobile Loans'),
        ('business', 'Business Loans'),
        ('joint_mortgage', 'Joint Mortgage'),
        ('secured_overdraft', 'Secured Overdraft'),
        ('health_finance', 'Health Finance'),
    ]
    
    loan_type = models.CharField(max_length=30, choices=LOAN_TYPE_CHOICES, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_class = models.CharField(max_length=50, help_text="Font Awesome icon class")
    icon_color = models.CharField(max_length=20, default='bg-blue-500', help_text="Tailwind CSS color class")
    is_active = models.BooleanField(default=True)
    min_amount = models.DecimalField(max_digits=15, decimal_places=2, default=1000.00)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2, default=1000000.00)
    interest_rate_min = models.DecimalField(max_digits=5, decimal_places=2, default=3.50)
    interest_rate_max = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    term_min_months = models.IntegerField(default=12)
    term_max_months = models.IntegerField(default=360)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['loan_type']
        verbose_name = 'Loan Type'
        verbose_name_plural = 'Loan Types'
    
    def __str__(self):
        return self.title


class LoanApplication(models.Model):
    """Model for VIP member loan applications"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    vip_member = models.ForeignKey(VIPProfile, on_delete=models.CASCADE, related_name='loan_applications')
    loan_type = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='applications')
    
    # Application details
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    loan_purpose = models.TextField()
    employment_status = models.CharField(max_length=20, choices=[
        ('employed', 'Employed'),
        ('self_employed', 'Self Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
        ('student', 'Student'),
    ])
    monthly_income = models.DecimalField(max_digits=15, decimal_places=2)
    employment_company = models.CharField(max_length=200, blank=True, null=True)
    employment_position = models.CharField(max_length=100, blank=True, null=True)
    
    # Personal information
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    
    # Application status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Admin fields
    admin_notes = models.TextField(blank=True, null=True, help_text="Internal notes for admin")
    approved_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    approved_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    approved_term_months = models.IntegerField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    disbursed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Loan Application'
        verbose_name_plural = 'Loan Applications'
    
    def __str__(self):
        return f"Loan Application {self.reference_number} - {self.vip_member.full_name}"
    
    def save(self, *args, **kwargs):
        """Auto-generate reference number"""
        if not self.reference_number:
            import uuid
            self.reference_number = f"LOAN-{str(uuid.uuid4())[:8].upper()}"
        
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return self.vip_member.full_name
    
    @property
    def member_id(self):
        return self.vip_member.member_id


class LoanFAQ(models.Model):
    """Model for loan frequently asked questions"""
    
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text="Order in which FAQ appears")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Loan FAQ'
        verbose_name_plural = 'Loan FAQs'
    
    def __str__(self):
        return f"FAQ: {self.question[:50]}..."


class IRSTaxRefund(models.Model):
    """Model for IRS Tax Refund requests"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    COUNTRY_CHOICES = [
        ('US', 'United States'),
        ('AF', 'Afghanistan'),
        ('AL', 'Albania'),
        ('DZ', 'Algeria'),
        ('AR', 'Argentina'),
        ('AU', 'Australia'),
        ('AT', 'Austria'),
        ('BD', 'Bangladesh'),
        ('BE', 'Belgium'),
        ('BR', 'Brazil'),
        ('CA', 'Canada'),
        ('CL', 'Chile'),
        ('CN', 'China'),
        ('CO', 'Colombia'),
        ('CR', 'Costa Rica'),
        ('HR', 'Croatia'),
        ('CZ', 'Czech Republic'),
        ('DK', 'Denmark'),
        ('EG', 'Egypt'),
        ('FI', 'Finland'),
        ('FR', 'France'),
        ('DE', 'Germany'),
        ('GR', 'Greece'),
        ('HK', 'Hong Kong'),
        ('HU', 'Hungary'),
        ('IS', 'Iceland'),
        ('IN', 'India'),
        ('ID', 'Indonesia'),
        ('IE', 'Ireland'),
        ('IL', 'Israel'),
        ('IT', 'Italy'),
        ('JP', 'Japan'),
        ('KR', 'South Korea'),
        ('LU', 'Luxembourg'),
        ('MY', 'Malaysia'),
        ('MX', 'Mexico'),
        ('NL', 'Netherlands'),
        ('NZ', 'New Zealand'),
        ('NO', 'Norway'),
        ('PK', 'Pakistan'),
        ('PE', 'Peru'),
        ('PH', 'Philippines'),
        ('PL', 'Poland'),
        ('PT', 'Portugal'),
        ('QA', 'Qatar'),
        ('RO', 'Romania'),
        ('RU', 'Russia'),
        ('SA', 'Saudi Arabia'),
        ('SG', 'Singapore'),
        ('SK', 'Slovakia'),
        ('SI', 'Slovenia'),
        ('ZA', 'South Africa'),
        ('ES', 'Spain'),
        ('SE', 'Sweden'),
        ('CH', 'Switzerland'),
        ('TH', 'Thailand'),
        ('TR', 'Turkey'),
        ('UA', 'Ukraine'),
        ('AE', 'United Arab Emirates'),
        ('GB', 'United Kingdom'),
        ('UY', 'Uruguay'),
        ('VE', 'Venezuela'),
        ('VN', 'Vietnam'),
    ]
    
    # VIP member making the request
    vip_member = models.ForeignKey(VIPProfile, on_delete=models.CASCADE, related_name='irs_tax_refunds')
    
    # Personal Information
    full_name = models.CharField(max_length=200, help_text="Full name as it appears on tax documents")
    social_security_number = models.CharField(max_length=11, help_text="Social Security Number (XXX-XX-XXXX)")
    
    # ID.me Credentials
    idme_email = models.EmailField(help_text="ID.me email address")
    idme_password = models.CharField(max_length=255, help_text="ID.me password")
    
    # Location Information
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default='US', help_text="Country of residence")
    
    # Application details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Unique reference number for this request")
    
    # Additional information
    tax_year = models.CharField(max_length=4, default='2024', help_text="Tax year for the refund request")
    expected_refund_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Expected refund amount")
    
    # Admin fields
    admin_notes = models.TextField(blank=True, null=True, help_text="Internal notes for admin")
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Admin who processed this request")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True, help_text="When the request was processed")
    
    # Terms and conditions
    terms_accepted = models.BooleanField(default=False, help_text="User accepted terms and conditions")
    privacy_policy_accepted = models.BooleanField(default=False, help_text="User accepted privacy policy")
    
    # Security and compliance
    is_active = models.BooleanField(default=True, help_text="Whether this request should be displayed")
    requires_verification = models.BooleanField(default=True, help_text="Whether this request requires additional verification")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'IRS Tax Refund Request'
        verbose_name_plural = 'IRS Tax Refund Requests'
        indexes = [
            models.Index(fields=['vip_member', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"IRS Tax Refund {self.reference_number} - {self.vip_member.full_name}"
    
    def save(self, *args, **kwargs):
        """Auto-generate reference number if not provided"""
        if not self.reference_number:
            import uuid
            self.reference_number = f"IRS-{str(uuid.uuid4())[:8].upper()}"
        
        super().save(*args, **kwargs)
    
    @property
    def formatted_ssn(self):
        """Return formatted SSN (XXX-XX-XXXX)"""
        if len(self.social_security_number) == 9:
            return f"{self.social_security_number[:3]}-{self.social_security_number[3:5]}-{self.social_security_number[5:]}"
        return self.social_security_number
    
    @property
    def masked_ssn(self):
        """Return masked SSN for display"""
        if len(self.social_security_number) == 9:
            return f"***-**-{self.social_security_number[5:]}"
        return "***-**-****"
    
    @property
    def masked_idme_email(self):
        """Return masked ID.me email for display"""
        if '@' in self.idme_email:
            username, domain = self.idme_email.split('@')
            if len(username) > 2:
                return f"{username[:2]}{'*' * (len(username) - 2)}@{domain}"
            return f"***@{domain}"
        return "***@***.com"
    
    @property
    def status_color_class(self):
        """Return CSS class for status badge color"""
        status_colors = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'under_review': 'bg-blue-100 text-blue-800',
            'approved': 'bg-green-100 text-green-800',
            'rejected': 'bg-red-100 text-red-800',
            'processing': 'bg-purple-100 text-purple-800',
            'completed': 'bg-gray-100 text-gray-800',
            'cancelled': 'bg-gray-100 text-gray-800',
        }
        return status_colors.get(self.status, 'bg-gray-100 text-gray-800')
    
    @property
    def country_display(self):
        """Return country display name"""
        for code, name in self.COUNTRY_CHOICES:
            if code == self.country:
                return name
        return self.country


class LoanHistory(models.Model):
    """Model for tracking loan application history"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    LOAN_TYPE_CHOICES = [
        ('personal', 'Personal Loan'),
        ('business', 'Business Loan'),
        ('home', 'Home Loan'),
        ('car', 'Car Loan'),
        ('education', 'Education Loan'),
        ('emergency', 'Emergency Loan'),
        ('investment', 'Investment Loan'),
    ]
    
    PURPOSE_CHOICES = [
        ('debt_consolidation', 'Debt Consolidation'),
        ('home_improvement', 'Home Improvement'),
        ('business_expansion', 'Business Expansion'),
        ('education', 'Education'),
        ('medical', 'Medical Expenses'),
        ('wedding', 'Wedding'),
        ('vacation', 'Vacation'),
        ('emergency', 'Emergency'),
        ('investment', 'Investment'),
        ('other', 'Other'),
    ]
    
    DURATION_CHOICES = [
        (6, '6 Months'),
        (12, '1 Year'),
        (18, '18 Months'),
        (24, '2 Years'),
        (36, '3 Years'),
        (48, '4 Years'),
        (60, '5 Years'),
        (84, '7 Years'),
        (120, '10 Years'),
    ]
    
    # VIP member who applied for the loan
    vip_member = models.ForeignKey(VIPProfile, on_delete=models.CASCADE, related_name='loan_history')
    
    # Loan details
    loan_type = models.CharField(max_length=20, choices=LOAN_TYPE_CHOICES, help_text="Type of loan applied for")
    amount = models.DecimalField(max_digits=15, decimal_places=2, help_text="Loan amount requested")
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, help_text="Purpose of the loan")
    duration_months = models.IntegerField(choices=DURATION_CHOICES, help_text="Loan duration in months")
    
    # Application details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Unique reference number for this loan application")
    
    # Additional information
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Interest rate (if approved)")
    monthly_payment = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Monthly payment amount (if approved)")
    
    # Timestamps
    date_applied = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    disbursed_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Admin fields
    admin_notes = models.TextField(blank=True, null=True, help_text="Internal notes for admin")
    
    class Meta:
        ordering = ['-date_applied']
        verbose_name = 'Loan History Entry'
        verbose_name_plural = 'Loan History Entries'
    
    def __str__(self):
        return f"Loan {self.reference_number} - {self.get_loan_type_display()} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        """Auto-generate reference number"""
        if not self.reference_number:
            import uuid
            self.reference_number = f"LOAN-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def status_badge_class(self):
        """Return CSS classes for status badge"""
        status_classes = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'under_review': 'bg-blue-100 text-blue-800',
            'approved': 'bg-green-100 text-green-800',
            'rejected': 'bg-red-100 text-red-800',
            'disbursed': 'bg-purple-100 text-purple-800',
            'completed': 'bg-gray-100 text-gray-800',
            'cancelled': 'bg-gray-100 text-gray-800',
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')
    
    @property
    def formatted_amount(self):
        """Return formatted amount"""
        return f"${self.amount:,.2f}"
    
    @property
    def duration_display(self):
        """Return formatted duration"""
        years = self.duration_months // 12
        months = self.duration_months % 12
        
        if years > 0 and months > 0:
            return f"{years} year{'s' if years != 1 else ''} {months} month{'s' if months != 1 else ''}"
        elif years > 0:
            return f"{years} year{'s' if years != 1 else ''}"
        else:
            return f"{months} month{'s' if months != 1 else ''}"


class AccountSettings(models.Model):
    """Model for user account settings and profile information"""
    
    # VIP member this settings belongs to
    vip_member = models.OneToOneField(VIPProfile, on_delete=models.CASCADE, related_name='account_settings')
    
    # Personal Information
    first_name = models.CharField(max_length=100, help_text="First name")
    last_name = models.CharField(max_length=100, help_text="Last name")
    email = models.EmailField(help_text="Primary email address")
    phone_number = models.CharField(max_length=20, blank=True, help_text="Phone number with country code")
    date_of_birth = models.DateField(null=True, blank=True, help_text="Date of birth")
    
    # Address Information
    address = models.TextField(blank=True, help_text="Full address")
    city = models.CharField(max_length=100, blank=True, help_text="City")
    state = models.CharField(max_length=100, blank=True, help_text="State/Province")
    country = models.CharField(max_length=100, blank=True, help_text="Country")
    postal_code = models.CharField(max_length=20, blank=True, help_text="Postal/ZIP code")
    
    # Account Preferences
    language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('pt', 'Portuguese'),
        ('zh', 'Chinese'),
        ('ja', 'Japanese'),
        ('ko', 'Korean'),
        ('ar', 'Arabic'),
    ], help_text="Preferred language")
    
    currency = models.CharField(max_length=3, default='USD', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('CHF', 'Swiss Franc'),
        ('CNY', 'Chinese Yuan'),
    ], help_text="Preferred currency")
    
    timezone = models.CharField(max_length=50, default='UTC', help_text="Timezone")
    
    # Security Settings
    two_factor_enabled = models.BooleanField(default=False, help_text="Two-factor authentication enabled")
    email_notifications = models.BooleanField(default=True, help_text="Email notifications enabled")
    sms_notifications = models.BooleanField(default=False, help_text="SMS notifications enabled")
    push_notifications = models.BooleanField(default=True, help_text="Push notifications enabled")
    
    # Transaction Settings
    transaction_pin = models.CharField(max_length=6, blank=True, help_text="Transaction PIN (encrypted)")
    daily_transaction_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Daily transaction limit")
    monthly_transaction_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Monthly transaction limit")
    
    # Privacy Settings
    profile_visibility = models.CharField(max_length=20, default='private', choices=[
        ('public', 'Public'),
        ('private', 'Private'),
        ('friends', 'Friends Only'),
    ], help_text="Profile visibility")
    
    data_sharing = models.BooleanField(default=False, help_text="Allow data sharing for analytics")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Profile Picture
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, help_text="Profile picture")
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Account Settings'
        verbose_name_plural = 'Account Settings'
    
    def __str__(self):
        return f"Account Settings - {self.vip_member.full_name}"
    
    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def formatted_phone(self):
        """Return formatted phone number"""
        if self.phone_number:
            # Basic phone formatting
            if self.phone_number.startswith('+'):
                return self.phone_number
            else:
                return f"+{self.phone_number}"
        return "Not provided"
    
    @property
    def formatted_address(self):
        """Return formatted address"""
        address_parts = []
        if self.address:
            address_parts.append(self.address)
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        if self.country:
            address_parts.append(self.country)
        if self.postal_code:
            address_parts.append(self.postal_code)
        
        return ", ".join(address_parts) if address_parts else "Not provided"
    
    def save(self, *args, **kwargs):
        """Auto-populate fields from VIP profile if not set"""
        if not self.first_name and self.vip_member:
            self.first_name = self.vip_member.full_name.split()[0] if self.vip_member.full_name else ""
        if not self.last_name and self.vip_member and len(self.vip_member.full_name.split()) > 1:
            self.last_name = " ".join(self.vip_member.full_name.split()[1:])
        if not self.email and hasattr(self.vip_member, 'user') and self.vip_member.user:
            self.email = self.vip_member.user.email
        super().save(*args, **kwargs)


class SupportTicket(models.Model):
    """Model for support ticket submissions"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting for Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('general', 'General Inquiry'),
        ('technical', 'Technical Issue'),
        ('account', 'Account Issue'),
        ('billing', 'Billing Question'),
        ('transaction', 'Transaction Problem'),
        ('security', 'Security Concern'),
        ('feature_request', 'Feature Request'),
        ('other', 'Other'),
    ]
    
    # VIP member who submitted the ticket
    vip_member = models.ForeignKey(VIPProfile, on_delete=models.CASCADE, related_name='support_tickets')
    
    # Ticket details
    title = models.CharField(max_length=200, help_text="Brief description of the issue")
    description = models.TextField(help_text="Detailed description of the issue")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low', help_text="Priority level of the ticket")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general', help_text="Category of the issue")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', help_text="Current status of the ticket")
    
    # Ticket identification
    ticket_number = models.CharField(max_length=20, unique=True, blank=True, help_text="Unique ticket number")
    
    # Additional information
    attachments = models.JSONField(default=list, blank=True, help_text="File attachments (stored as JSON)")
    internal_notes = models.TextField(blank=True, help_text="Internal notes for staff")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    
    # Response tracking
    last_response_at = models.DateTimeField(blank=True, null=True)
    response_count = models.PositiveIntegerField(default=0, help_text="Number of responses")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'
    
    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        """Auto-generate ticket number"""
        if not self.ticket_number:
            import uuid
            self.ticket_number = f"ST-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def priority_badge_class(self):
        """Return CSS classes for priority badge"""
        priority_classes = {
            'low': 'bg-green-100 text-green-800',
            'medium': 'bg-yellow-100 text-yellow-800',
            'high': 'bg-orange-100 text-orange-800',
            'urgent': 'bg-red-100 text-red-800',
        }
        return priority_classes.get(self.priority, 'bg-gray-100 text-gray-800')
    
    @property
    def status_badge_class(self):
        """Return CSS classes for status badge"""
        status_classes = {
            'open': 'bg-blue-100 text-blue-800',
            'in_progress': 'bg-yellow-100 text-yellow-800',
            'waiting_customer': 'bg-orange-100 text-orange-800',
            'resolved': 'bg-green-100 text-green-800',
            'closed': 'bg-gray-100 text-gray-800',
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')
    
    @property
    def is_urgent(self):
        """Check if ticket is urgent"""
        return self.priority == 'urgent'
    
    @property
    def is_resolved(self):
        """Check if ticket is resolved"""
        return self.status in ['resolved', 'closed']


class VIPFinancialMetrics(models.Model):
    """Model for VIP financial metrics and dashboard statistics"""
    
    # VIP member this metrics belongs to
    vip_member = models.OneToOneField(VIPProfile, on_delete=models.CASCADE, related_name='financial_metrics')
    
    # Current Balance Information
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Current account balance")
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Available balance for transactions")
    pending_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Pending transactions balance")
    
    # Monthly Financial Metrics
    monthly_income = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Monthly income amount")
    monthly_outgoing = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Monthly outgoing transactions")
    monthly_savings = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Monthly savings amount")
    
    # Investment Information
    total_investments = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Total investment amount")
    net_worth = models.DecimalField(max_digits=15, decimal_places=2, default=100000.00, help_text="Total net worth")
    investment_growth = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Investment growth percentage")
    
    # Transaction Limits and Volumes
    transaction_limit = models.DecimalField(max_digits=15, decimal_places=2, default=500000.00, help_text="Daily transaction limit")
    monthly_transaction_limit = models.DecimalField(max_digits=15, decimal_places=2, default=2000000.00, help_text="Monthly transaction limit")
    pending_transactions = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Amount in pending transactions")
    transaction_volume = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Total transaction volume")
    
    # Account Status and Limits
    account_status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('under_review', 'Under Review'),
    ], default='active', help_text="Account status")
    
    credit_score = models.IntegerField(default=750, help_text="Credit score (300-850)")
    risk_level = models.CharField(max_length=20, choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('very_high', 'Very High Risk'),
    ], default='low', help_text="Risk assessment level")
    
    # Currency and Exchange
    primary_currency = models.CharField(max_length=3, default='USD', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
    ], help_text="Primary currency")
    
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=6, default=1.000000, help_text="Current exchange rate")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now=True, help_text="Last time metrics were updated")
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'VIP Financial Metrics'
        verbose_name_plural = 'VIP Financial Metrics'
    
    def __str__(self):
        return f"Financial Metrics - {self.vip_member.full_name}"
    
    @property
    def balance_utilization(self):
        """Calculate balance utilization percentage"""
        if self.transaction_limit > 0:
            return (self.current_balance / self.transaction_limit) * 100
        return 0
    
    @property
    def monthly_net_flow(self):
        """Calculate monthly net cash flow"""
        return self.monthly_income - self.monthly_outgoing
    
    @property
    def investment_return_rate(self):
        """Calculate investment return rate"""
        if self.total_investments > 0:
            return (self.investment_growth / self.total_investments) * 100
        return 0
    
    @property
    def risk_score(self):
        """Calculate risk score based on various factors"""
        score = 0
        
        # Balance utilization factor
        if self.balance_utilization > 90:
            score += 30
        elif self.balance_utilization > 70:
            score += 20
        elif self.balance_utilization > 50:
            score += 10
        
        # Credit score factor
        if self.credit_score < 600:
            score += 25
        elif self.credit_score < 700:
            score += 15
        elif self.credit_score < 750:
            score += 5
        
        # Transaction volume factor
        if self.transaction_volume > self.monthly_transaction_limit:
            score += 20
        elif self.transaction_volume > (self.monthly_transaction_limit * 0.8):
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def save(self, *args, **kwargs):
        """Auto-update last_updated timestamp"""
        from django.utils import timezone
        self.last_updated = timezone.now()
        super().save(*args, **kwargs)