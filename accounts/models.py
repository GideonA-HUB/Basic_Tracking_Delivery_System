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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Card information
    card_name = models.CharField(max_length=100, help_text="Name on the card")
    expiry_month = models.CharField(max_length=2, help_text="Expiry month (01-12)")
    expiry_year = models.CharField(max_length=4, help_text="Expiry year (YYYY)")
    
    # Financial details
    spending_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Monthly spending limit")
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Current card balance")
    currency = models.CharField(max_length=3, default='USD', help_text="Currency code")
    
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
    
    def save(self, *args, **kwargs):
        """Auto-set expiry_date based on expiry_month and expiry_year"""
        if self.expiry_month and self.expiry_year:
            from datetime import datetime
            try:
                self.expiry_date = datetime(int(self.expiry_year), int(self.expiry_month), 1)
            except (ValueError, TypeError):
                pass
        super().save(*args, **kwargs)