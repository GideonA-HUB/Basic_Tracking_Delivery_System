from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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


@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    """Create staff profile when user is created"""
    if created and instance.is_staff:
        StaffProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_staff_profile(sender, instance, **kwargs):
    """Save staff profile when user is saved"""
    if hasattr(instance, 'staff_profile'):
        instance.staff_profile.save()
