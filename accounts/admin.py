from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import StaffProfile, CustomerProfile, VIPProfile, RecentActivity, Transaction, Card, LocalTransfer, InternationalTransfer, Deposit, Loan, LoanApplication, LoanFAQ


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


class CardInline(admin.TabularInline):
    """Inline admin for Card"""
    model = Card
    extra = 0
    fields = ('card_name', 'card_number', 'card_brand', 'card_level', 'status', 'current_balance', 'daily_spending_limit', 'is_active')
    readonly_fields = ('created_at', 'updated_at')


class LocalTransferInline(admin.TabularInline):
    """Inline admin for LocalTransfer"""
    model = LocalTransfer
    extra = 0
    fields = ('reference_number', 'transfer_amount', 'beneficiary_name', 'status', 'transfer_date', 'is_active')
    readonly_fields = ('created_at', 'updated_at')


class InternationalTransferInline(admin.TabularInline):
    """Inline admin for InternationalTransfer"""
    model = InternationalTransfer
    extra = 0
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
    fields = (
        'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 
        'status', 'reference_number', 'transfer_fee', 'total_amount', 
        'transfer_date', 'created_at'
    )


@admin.register(VIPProfile)
class VIPProfileAdmin(admin.ModelAdmin):
    """Admin for VIPProfile"""
    list_display = ('user', 'member_id', 'membership_tier', 'status', 'assigned_staff', 'total_investments', 'created_at')
    list_filter = ('membership_tier', 'status', 'assigned_staff', 'priority_support', 'dedicated_account_manager', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'member_id', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'membership_start_date')
    inlines = [RecentActivityInline, TransactionInline, CardInline, LocalTransferInline, InternationalTransferInline]
    
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


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    """Admin for Card"""
    list_display = ('vip_member', 'card_name', 'card_number', 'card_brand', 'card_level', 'status', 'formatted_balance', 'formatted_spending_limit', 'formatted_expiry_date', 'is_active')
    list_filter = ('card_brand', 'card_level', 'status', 'currency', 'is_active', 'issue_date', 'expiry_date', 'created_at')
    search_fields = ('vip_member__user__username', 'vip_member__user__first_name', 'vip_member__user__last_name', 
                     'card_name', 'card_number', 'description', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    date_hierarchy = 'issue_date'
    
    fieldsets = (
            ('Card Information', {
                'fields': ('vip_member', 'card_name', 'card_number', 'card_brand', 'card_level', 'description')
            }),
            ('Card Details', {
                'fields': ('expiry_month', 'expiry_year', 'expiry_date', 'status')
            }),
            ('Financial Details', {
                'fields': ('spending_limit', 'daily_spending_limit', 'current_balance', 'currency')
            }),
            ('Application Details', {
                'fields': ('cardholder_name', 'billing_address', 'application_fee', 'terms_accepted')
            }),
            ('Additional Information', {
                'fields': ('notes',),
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
    
    def formatted_balance(self, obj):
        """Display formatted balance with color"""
        return f'<span style="color: green;">{obj.formatted_balance}</span>'
    formatted_balance.allow_tags = True
    formatted_balance.short_description = 'Balance'
    
    def formatted_spending_limit(self, obj):
        """Display formatted spending limit"""
        return obj.formatted_spending_limit
    formatted_spending_limit.short_description = 'Spending Limit'
    
    def formatted_expiry_date(self, obj):
        """Display formatted expiry date"""
        return obj.formatted_expiry_date
    formatted_expiry_date.short_description = 'Expires'
    
    def save_model(self, request, obj, form, change):
        """Auto-set expiry_date based on expiry_month and expiry_year"""
        if obj.expiry_month and obj.expiry_year:
            from datetime import datetime
            try:
                obj.expiry_date = datetime(int(obj.expiry_year), int(obj.expiry_month), 1)
            except (ValueError, TypeError):
                pass
        super().save_model(request, obj, form, change)


@admin.register(LocalTransfer)
class LocalTransferAdmin(admin.ModelAdmin):
    """Admin for LocalTransfer"""
    list_display = ('vip_member', 'reference_number', 'formatted_amount', 'beneficiary_name', 'bank_name', 'status', 'transfer_date', 'is_active')
    list_filter = ('status', 'transfer_type', 'currency', 'is_active', 'transfer_date', 'created_at')
    search_fields = ('vip_member__user__username', 'vip_member__user__first_name', 'vip_member__user__last_name', 
                     'reference_number', 'beneficiary_name', 'beneficiary_account_number', 'bank_name')
    readonly_fields = ('created_at', 'updated_at', 'reference_number', 'total_amount')
    list_editable = ('is_active',)
    date_hierarchy = 'transfer_date'
    
    fieldsets = (
        ('Transfer Information', {
            'fields': ('vip_member', 'reference_number', 'transfer_amount', 'currency', 'transfer_type')
        }),
        ('Beneficiary Details', {
            'fields': ('beneficiary_name', 'beneficiary_account_number', 'bank_name')
        }),
        ('Transfer Details', {
            'fields': ('status', 'transfer_fee', 'total_amount', 'transfer_date', 'processed_date')
        }),
        ('Additional Information', {
            'fields': ('description', 'notes'),
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
        return f'<span style="color: green;">{obj.formatted_amount}</span>'
    formatted_amount.allow_tags = True
    formatted_amount.short_description = 'Amount'
    
    def save_model(self, request, obj, form, change):
        """Auto-generate reference_number if not provided"""
        if not obj.reference_number:
            import uuid
            obj.reference_number = f"LT-{str(uuid.uuid4())[:8].upper()}"
        super().save_model(request, obj, form, change)


@admin.register(InternationalTransfer)
class InternationalTransferAdmin(admin.ModelAdmin):
    """Admin interface for InternationalTransfer"""
    list_display = (
        'reference_number', 'vip_member', 'transfer_method', 'transfer_amount', 
        'currency', 'recipient_name', 'status', 'transfer_fee', 'total_amount', 
        'transfer_date', 'created_at'
    )
    list_filter = (
        'status', 'transfer_method', 'currency', 'transfer_date', 'created_at'
    )
    search_fields = (
        'reference_number', 'vip_member__user__username', 'vip_member__user__first_name',
        'vip_member__user__last_name', 'recipient_name', 'recipient_email',
        'bank_name', 'tracking_number'
    )
    readonly_fields = (
        'reference_number', 'tracking_number', 'created_at', 'updated_at',
        'processed_date', 'completed_date'
    )
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transfer Information', {
            'fields': (
                'vip_member', 'transfer_method', 'transfer_amount', 'currency',
                'reference_number', 'tracking_number', 'status'
            )
        }),
        ('Recipient Details', {
            'fields': (
                'recipient_name', 'recipient_email', 'recipient_phone'
            )
        }),
        ('Bank Details', {
            'fields': (
                'bank_name', 'bank_address', 'account_number', 'routing_number',
                'swift_code', 'iban'
            ),
            'classes': ('collapse',)
        }),
        ('Wallet Details', {
            'fields': (
                'wallet_address', 'wallet_type'
            ),
            'classes': ('collapse',)
        }),
        ('Transfer Details', {
            'fields': (
                'purpose_of_transfer', 'description'
            )
        }),
        ('Fees and Amounts', {
            'fields': (
                'transfer_fee', 'exchange_rate', 'total_amount'
            )
        }),
        ('Dates', {
            'fields': (
                'transfer_date', 'processed_date', 'completed_date',
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': (
                'notes', 'compliance_notes', 'requires_approval', 'is_active'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter transfers for current VIP member"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(vip_member__user=request.user)


# Admin classes are registered using decorators above


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    """Admin configuration for Deposit model"""
    
    list_display = [
        'reference_number', 'vip_member', 'deposit_method', 'amount', 'currency', 
        'status', 'created_at', 'processed_at'
    ]
    
    list_filter = [
        'deposit_method', 'status', 'currency', 'created_at'
    ]
    
    search_fields = [
        'reference_number', 'vip_member__full_name', 'vip_member__member_id',
        'transaction_id', 'notes'
    ]
    
    readonly_fields = [
        'reference_number', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Deposit Information', {
            'fields': (
                'reference_number', 'vip_member', 'deposit_method', 'amount', 'currency'
            )
        }),
        ('Status & Processing', {
            'fields': (
                'status', 'transaction_id', 'processed_at'
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes', 'admin_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processing', 'mark_as_completed', 'mark_as_failed']
    
    def mark_as_processing(self, request, queryset):
        """Mark selected deposits as processing"""
        from django.utils import timezone
        updated = queryset.update(status='processing', processed_at=timezone.now())
        self.message_user(request, f'{updated} deposits marked as processing.')
    mark_as_processing.short_description = "Mark selected deposits as processing"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected deposits as completed"""
        from django.utils import timezone
        updated = queryset.update(status='completed', processed_at=timezone.now())
        self.message_user(request, f'{updated} deposits marked as completed.')
    mark_as_completed.short_description = "Mark selected deposits as completed"
    
    def mark_as_failed(self, request, queryset):
        """Mark selected deposits as failed"""
        from django.utils import timezone
        updated = queryset.update(status='failed', processed_at=timezone.now())
        self.message_user(request, f'{updated} deposits marked as failed.')
    mark_as_failed.short_description = "Mark selected deposits as failed"
    
    def get_queryset(self, request):
        """Filter deposits for current VIP member if not superuser"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            vip_profile = request.user.vip_profile
            return qs.filter(vip_member=vip_profile)
        except:
            return qs.none()
    
    def has_change_permission(self, request, obj=None):
        """Allow VIP members to view their own deposits"""
        if obj and hasattr(request.user, 'vip_profile'):
            return obj.vip_member == request.user.vip_profile
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete deposits"""
        return request.user.is_superuser


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """Admin configuration for Loan model"""
    
    list_display = [
        'title', 'loan_type', 'min_amount', 'max_amount', 
        'interest_rate_min', 'interest_rate_max', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'loan_type', 'is_active', 'created_at'
    ]
    
    search_fields = [
        'title', 'description', 'loan_type'
    ]
    
    fieldsets = (
        ('Loan Information', {
            'fields': (
                'loan_type', 'title', 'description', 'is_active'
            )
        }),
        ('Visual Settings', {
            'fields': (
                'icon_class', 'icon_color'
            )
        }),
        ('Loan Terms', {
            'fields': (
                'min_amount', 'max_amount', 'interest_rate_min', 
                'interest_rate_max', 'term_min_months', 'term_max_months'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    """Admin configuration for LoanApplication model"""
    
    list_display = [
        'reference_number', 'vip_member', 'loan_type', 'loan_amount', 
        'status', 'created_at', 'approved_at'
    ]
    
    list_filter = [
        'status', 'loan_type__loan_type', 'employment_status', 'created_at', 'approved_at'
    ]
    
    search_fields = [
        'reference_number', 'vip_member__full_name', 'vip_member__member_id',
        'employment_company', 'phone_number', 'city', 'state'
    ]
    
    readonly_fields = [
        'reference_number', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Application Information', {
            'fields': (
                'reference_number', 'vip_member', 'loan_type', 'loan_amount', 'loan_purpose'
            )
        }),
        ('Employment Details', {
            'fields': (
                'employment_status', 'monthly_income', 'employment_company', 'employment_position'
            )
        }),
        ('Contact Information', {
            'fields': (
                'phone_number', 'address', 'city', 'state', 'zip_code', 'country'
            )
        }),
        ('Status & Processing', {
            'fields': (
                'status', 'admin_notes'
            )
        }),
        ('Approval Details', {
            'fields': (
                'approved_amount', 'approved_interest_rate', 'approved_term_months'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'reviewed_at', 'approved_at', 'disbursed_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_under_review', 'mark_as_approved', 'mark_as_rejected']
    
    def mark_as_under_review(self, request, queryset):
        """Mark selected applications as under review"""
        from django.utils import timezone
        updated = queryset.update(status='under_review', reviewed_at=timezone.now())
        self.message_user(request, f'{updated} applications marked as under review.')
    mark_as_under_review.short_description = "Mark selected applications as under review"
    
    def mark_as_approved(self, request, queryset):
        """Mark selected applications as approved"""
        from django.utils import timezone
        updated = queryset.update(status='approved', approved_at=timezone.now())
        self.message_user(request, f'{updated} applications marked as approved.')
    mark_as_approved.short_description = "Mark selected applications as approved"
    
    def mark_as_rejected(self, request, queryset):
        """Mark selected applications as rejected"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} applications marked as rejected.')
    mark_as_rejected.short_description = "Mark selected applications as rejected"
    
    def get_queryset(self, request):
        """Filter applications for current VIP member if not superuser"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            vip_profile = request.user.vip_profile
            return qs.filter(vip_member=vip_profile)
        except:
            return qs.none()
    
    def has_change_permission(self, request, obj=None):
        """Allow VIP members to view their own applications"""
        if obj and hasattr(request.user, 'vip_profile'):
            return obj.vip_member == request.user.vip_profile
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete applications"""
        return request.user.is_superuser


@admin.register(LoanFAQ)
class LoanFAQAdmin(admin.ModelAdmin):
    """Admin configuration for LoanFAQ model"""
    
    list_display = [
        'question', 'order', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'created_at'
    ]
    
    search_fields = [
        'question', 'answer'
    ]
    
    fieldsets = (
        ('FAQ Content', {
            'fields': (
                'question', 'answer'
            )
        }),
        ('Display Settings', {
            'fields': (
                'order', 'is_active'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def mark_as_active(self, request, queryset):
        """Mark selected FAQs as active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} FAQs marked as active.')
    mark_as_active.short_description = "Mark selected FAQs as active"
    
    def mark_as_inactive(self, request, queryset):
        """Mark selected FAQs as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} FAQs marked as inactive.')
    mark_as_inactive.short_description = "Mark selected FAQs as inactive"
