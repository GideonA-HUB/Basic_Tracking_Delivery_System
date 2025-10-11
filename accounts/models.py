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
