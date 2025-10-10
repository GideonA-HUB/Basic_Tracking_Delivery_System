from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


class VIPStaff(models.Model):
    """VIP Staff members who can be assigned to VIP customers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vip_staff_profile')
    staff_id = models.CharField(max_length=20, unique=True, help_text="Unique staff identifier")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    department = models.CharField(max_length=50, default='VIP Services')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'VIP Staff Member'
        verbose_name_plural = 'VIP Staff Members'
        ordering = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} ({self.staff_id})"


class VIPMember(models.Model):
    """VIP Member profile with staff assignment"""
    
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
    
    # Customer information
    customer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vip_member_profile')
    member_id = models.CharField(max_length=20, unique=True, help_text="Unique VIP member identifier")
    
    # Staff assignment
    assigned_staff = models.ForeignKey(VIPStaff, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='assigned_members', help_text="VIP Staff member assigned to this customer")
    
    # Membership details
    membership_tier = models.CharField(max_length=20, choices=MEMBERSHIP_TIER_CHOICES, default='bronze')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Personal information
    phone = models.CharField(max_length=20, blank=True)
    preferred_contact_method = models.CharField(max_length=20, 
                                              choices=[('email', 'Email'), ('phone', 'Phone'), ('both', 'Both')],
                                              default='email')
    
    # VIP Benefits
    priority_support = models.BooleanField(default=True)
    dedicated_account_manager = models.BooleanField(default=True)
    exclusive_investment_opportunities = models.BooleanField(default=True)
    faster_processing = models.BooleanField(default=True)
    
    # Financial information
    total_investments = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    net_worth = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Timestamps
    membership_start_date = models.DateTimeField(default=timezone.now)
    last_contact_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes and comments
    notes = models.TextField(blank=True, help_text="Internal notes about the VIP member")
    
    class Meta:
        verbose_name = 'VIP Member'
        verbose_name_plural = 'VIP Members'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.get_membership_tier_display()}"
    
    @property
    def full_name(self):
        return f"{self.customer.first_name} {self.customer.last_name}".strip() or self.customer.username
    
    @property
    def staff_name(self):
        return self.assigned_staff.full_name if self.assigned_staff else "Not Assigned"
    
    @property
    def membership_duration_days(self):
        return (timezone.now() - self.membership_start_date).days


class VIPActivity(models.Model):
    """Track VIP member activities and interactions"""
    
    ACTIVITY_TYPE_CHOICES = [
        ('login', 'Dashboard Login'),
        ('investment', 'Investment Activity'),
        ('withdrawal', 'Withdrawal Request'),
        ('support', 'Support Contact'),
        ('meeting', 'Staff Meeting'),
        ('call', 'Phone Call'),
        ('email', 'Email Communication'),
        ('other', 'Other'),
    ]
    
    member = models.ForeignKey(VIPMember, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    staff_member = models.ForeignKey(VIPStaff, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_important = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'VIP Activity'
        verbose_name_plural = 'VIP Activities'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.member.full_name} - {self.title}"


class VIPBenefit(models.Model):
    """VIP Benefits and privileges"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    membership_tiers = models.CharField(max_length=200, help_text="Comma-separated list of membership tiers (bronze,silver,gold,platinum,diamond)")
    icon = models.CharField(max_length=50, default='fas fa-star')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'VIP Benefit'
        verbose_name_plural = 'VIP Benefits'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def applicable_tiers(self):
        return [tier.strip() for tier in self.membership_tiers.split(',')]


class VIPApplication(models.Model):
    """VIP membership applications that require admin approval"""
    
    APPLICATION_STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('requires_info', 'Requires Additional Information'),
    ]
    
    MEMBERSHIP_TIER_CHOICES = [
        ('bronze', 'Bronze VIP'),
        ('silver', 'Silver VIP'),
        ('gold', 'Gold VIP'),
        ('platinum', 'Platinum VIP'),
        ('diamond', 'Diamond VIP'),
    ]
    
    # Applicant information
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vip_applications')
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='pending')
    requested_tier = models.CharField(max_length=20, choices=MEMBERSHIP_TIER_CHOICES, default='bronze')
    
    # Application details
    reason_for_application = models.TextField(help_text="Why do you want to become a VIP member?")
    investment_experience = models.TextField(help_text="Describe your investment experience")
    expected_monthly_investment = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Expected monthly investment amount")
    net_worth_range = models.CharField(max_length=50, help_text="Estimated net worth range")
    
    # Contact preferences
    preferred_contact_method = models.CharField(max_length=20, 
                                              choices=[('email', 'Email'), ('phone', 'Phone'), ('both', 'Both')],
                                              default='email')
    phone = models.CharField(max_length=20, blank=True)
    
    # Admin review
    assigned_reviewer = models.ForeignKey(VIPStaff, on_delete=models.SET_NULL, null=True, blank=True, 
                                        related_name='reviewed_applications')
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admin review")
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection (if applicable)")
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'VIP Application'
        verbose_name_plural = 'VIP Applications'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.get_requested_tier_display()} ({self.get_status_display()})"
    
    @property
    def applicant_name(self):
        return f"{self.customer.first_name} {self.customer.last_name}".strip() or self.customer.username
    
    @property
    def is_pending(self):
        return self.status in ['pending', 'under_review']
    
    @property
    def is_approved(self):
        return self.status == 'approved'
    
    @property
    def is_rejected(self):
        return self.status == 'rejected'


class VIPNotification(models.Model):
    """VIP-specific notifications"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('promotion', 'Promotion'),
    ]
    
    member = models.ForeignKey(VIPMember, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'VIP Notification'
        verbose_name_plural = 'VIP Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.member.full_name} - {self.title}"
