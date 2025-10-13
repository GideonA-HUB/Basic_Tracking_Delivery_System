from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import StaffProfile, CustomerProfile, VIPProfile, RecentActivity, Transaction


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


class RecentActivityInline(admin.TabularInline):
    """Inline admin for RecentActivity"""
    model = RecentActivity
    extra = 0
    fields = ('title', 'activity_type', 'amount', 'currency', 'status', 'activity_date', 'is_active', 'display_order')
    readonly_fields = ('created_at', 'updated_at')


class TransactionInline(admin.TabularInline):
    """Inline admin for Transaction"""
    model = Transaction
    extra = 0
    fields = ('reference_id', 'transaction_type', 'amount', 'currency', 'status', 'scope', 'transaction_date', 'is_active')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VIPProfile)
class VIPProfileAdmin(admin.ModelAdmin):
    """Admin for VIPProfile"""
    list_display = ('user', 'member_id', 'membership_tier', 'status', 'assigned_staff', 'total_investments', 'created_at')
    list_filter = ('membership_tier', 'status', 'assigned_staff', 'priority_support', 'dedicated_account_manager', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'member_id', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'membership_start_date')
    inlines = [RecentActivityInline, TransactionInline]
    
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


@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
    """Admin for RecentActivity"""
    list_display = ('vip_member', 'title', 'activity_type', 'formatted_amount', 'status', 'activity_date', 'is_active', 'display_order')
    list_filter = ('activity_type', 'status', 'direction', 'is_active', 'is_featured', 'activity_date', 'created_at')
    search_fields = ('vip_member__user__username', 'vip_member__user__first_name', 'vip_member__user__last_name', 
                     'title', 'description', 'reference_number')
    readonly_fields = ('created_at', 'updated_at', 'direction')
    list_editable = ('is_active', 'display_order')
    date_hierarchy = 'activity_date'
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('vip_member', 'activity_type', 'title', 'description')
        }),
        ('Transaction Details', {
            'fields': ('amount', 'currency', 'direction', 'reference_number')
        }),
        ('Status and Dates', {
            'fields': ('status', 'activity_date')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active', 'is_featured')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_amount(self, obj):
        """Display formatted amount with color"""
        if obj.amount >= 0:
            return f'<span style="color: green;">+${obj.amount:,.2f}</span>'
        else:
            return f'<span style="color: red;">-${abs(obj.amount):,.2f}</span>'
    formatted_amount.allow_tags = True
    formatted_amount.short_description = 'Amount'
    
    def save_model(self, request, obj, form, change):
        """Auto-set direction based on amount"""
        if obj.amount >= 0:
            obj.direction = 'incoming'
        else:
            obj.direction = 'outgoing'
        super().save_model(request, obj, form, change)
    


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin for Transaction"""
    list_display = ('vip_member', 'reference_id', 'transaction_type', 'formatted_amount', 'status', 'scope', 'transaction_date', 'is_active')
    list_filter = ('transaction_type', 'status', 'scope', 'currency', 'is_active', 'transaction_date', 'created_at')
    search_fields = ('vip_member__user__username', 'vip_member__user__first_name', 'vip_member__user__last_name', 
                     'reference_id', 'description', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'reference_id')
    list_editable = ('is_active',)
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('vip_member', 'reference_id', 'transaction_type', 'description')
        }),
        ('Financial Details', {
            'fields': ('amount', 'currency', 'status', 'scope')
        }),
        ('Dates', {
            'fields': ('transaction_date',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Admin Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_amount(self, obj):
        """Display formatted amount with color"""
        if obj.transaction_type in ['deposit', 'refund', 'dividend', 'interest', 'bonus', 'commission']:
            return f'<span style="color: green;">{obj.formatted_amount}</span>'
        elif obj.transaction_type in ['withdrawal', 'fee', 'payment']:
            return f'<span style="color: red;">{obj.formatted_amount}</span>'
        else:
            return f'<span style="color: gray;">{obj.formatted_amount}</span>'
    formatted_amount.allow_tags = True
    formatted_amount.short_description = 'Amount'
    
    def save_model(self, request, obj, form, change):
        """Auto-generate reference_id if not provided"""
        if not obj.reference_id:
            import uuid
            obj.reference_id = f"TXN-{str(uuid.uuid4())[:8].upper()}"
        super().save_model(request, obj, form, change)
    
