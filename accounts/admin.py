from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import StaffProfile, CustomerProfile, VIPProfile


class StaffProfileInline(admin.StackedInline):
    """Inline admin for StaffProfile"""
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Profile'
    fk_name = 'user'


class CustomerProfileInline(admin.StackedInline):
    """Inline admin for CustomerProfile"""
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'
    fk_name = 'user'


class VIPProfileInline(admin.StackedInline):
    """Inline admin for VIPProfile"""
    model = VIPProfile
    can_delete = False
    verbose_name_plural = 'VIP Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    """Custom User admin with StaffProfile, CustomerProfile, and VIPProfile inlines"""
    inlines = (StaffProfileInline, CustomerProfileInline, VIPProfileInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'staff_profile__role', 'staff_profile__is_active_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_role(self, obj):
        try:
            if obj.is_staff:
                return obj.staff_profile.get_role_display()
            else:
                return 'Customer'
        except (StaffProfile.DoesNotExist, CustomerProfile.DoesNotExist):
            return 'No Role'
    get_role.short_description = 'Role'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    """Admin for StaffProfile"""
    list_display = ('user', 'role', 'department', 'phone_number', 'is_active_staff', 'created_at')
    list_filter = ('role', 'department', 'is_active_staff', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'department')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'department')
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Status', {
            'fields': ('is_active_staff',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Admin for CustomerProfile"""
    list_display = ('user', 'phone_number', 'city', 'state', 'country', 'is_active_customer', 'created_at')
    list_filter = ('is_active_customer', 'city', 'state', 'country', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone_number', 'city', 'state')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth',)
        }),
        ('Status', {
            'fields': ('is_active_customer',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VIPProfile)
class VIPProfileAdmin(admin.ModelAdmin):
    """Admin for VIPProfile"""
    list_display = ('user', 'member_id', 'membership_tier', 'status', 'assigned_staff', 'total_investments', 'created_at')
    list_filter = ('membership_tier', 'status', 'assigned_staff', 'priority_support', 'dedicated_account_manager', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'member_id', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'membership_start_date')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'member_id')
        }),
        ('Membership Details', {
            'fields': ('membership_tier', 'status', 'assigned_staff')
        }),
        ('Contact Information', {
            'fields': ('phone', 'preferred_contact_method')
        }),
        ('VIP Benefits', {
            'fields': ('priority_support', 'dedicated_account_manager', 'exclusive_investment_opportunities', 'faster_processing')
        }),
        ('Financial Information', {
            'fields': ('total_investments', 'monthly_income', 'net_worth')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('membership_start_date', 'last_contact_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-generate member_id if not provided"""
        if not obj.member_id:
            import uuid
            obj.member_id = f"VIP-{str(uuid.uuid4())[:8].upper()}"
        super().save_model(request, obj, form, change)
