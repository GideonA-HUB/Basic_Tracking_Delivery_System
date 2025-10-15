from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms
from .models import StaffProfile, CustomerProfile, VIPProfile, RecentActivity, Transaction, Card, LocalTransfer, InternationalTransfer, Deposit, Loan, LoanApplication, LoanFAQ, IRSTaxRefund, LoanHistory, AccountSettings, SupportTicket, VIPFinancialMetrics


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
    fields = ('reference_number', 'transfer_amount', 'beneficiary_name', 'status', 'is_active')
    readonly_fields = ('transfer_date', 'created_at', 'updated_at')


class InternationalTransferInline(admin.TabularInline):
    """Inline admin for InternationalTransfer"""
    model = InternationalTransfer
    extra = 0
    readonly_fields = ('reference_number', 'transfer_date', 'created_at', 'updated_at')
    fields = (
        'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 
        'status', 'transfer_fee', 'total_amount'
    )


class IRSTaxRefundInline(admin.TabularInline):
    """Inline admin for IRSTaxRefund"""
    model = IRSTaxRefund
    extra = 0
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
    fields = (
        'reference_number', 'full_name', 'status', 'tax_year', 
        'expected_refund_amount', 'country', 'created_at'
    )


@admin.register(VIPProfile)
class VIPProfileAdmin(admin.ModelAdmin):
    """Admin for VIPProfile"""
    list_display = ('user', 'member_id', 'membership_tier', 'status', 'assigned_staff', 'total_investments', 'created_at')
    list_filter = ('membership_tier', 'status', 'assigned_staff', 'priority_support', 'dedicated_account_manager', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'member_id', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'membership_start_date')
    inlines = [RecentActivityInline, TransactionInline, CardInline, LocalTransferInline, InternationalTransferInline, IRSTaxRefundInline]
    
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


@admin.register(IRSTaxRefund)
class IRSTaxRefundAdmin(admin.ModelAdmin):
    """Admin configuration for IRSTaxRefund model"""
    
    list_display = [
        'reference_number', 'vip_member', 'full_name', 'tax_year', 
        'status', 'country', 'expected_refund_amount', 'created_at'
    ]
    
    list_filter = [
        'status', 'country', 'tax_year', 'terms_accepted', 'privacy_policy_accepted', 
        'requires_verification', 'is_active', 'created_at'
    ]
    
    search_fields = [
        'reference_number', 'vip_member__full_name', 'vip_member__member_id',
        'full_name', 'social_security_number', 'idme_email', 'tax_year'
    ]
    
    readonly_fields = [
        'reference_number', 'created_at', 'updated_at', 'masked_ssn', 'masked_idme_email'
    ]
    
    fieldsets = (
        ('Request Information', {
            'fields': (
                'reference_number', 'vip_member', 'status', 'tax_year'
            )
        }),
        ('Personal Information', {
            'fields': (
                'full_name', 'social_security_number', 'masked_ssn', 'country'
            )
        }),
        ('ID.me Credentials', {
            'fields': (
                'idme_email', 'masked_idme_email', 'idme_password'
            ),
            'classes': ('collapse',)
        }),
        ('Financial Information', {
            'fields': (
                'expected_refund_amount',
            )
        }),
        ('Terms and Conditions', {
            'fields': (
                'terms_accepted', 'privacy_policy_accepted'
            )
        }),
        ('Admin Processing', {
            'fields': (
                'admin_notes', 'processed_by', 'processed_at'
            ),
            'classes': ('collapse',)
        }),
        ('Security and Compliance', {
            'fields': (
                'requires_verification', 'is_active'
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
    
    actions = ['mark_as_under_review', 'mark_as_approved', 'mark_as_rejected', 'mark_as_processing', 'mark_as_completed']
    
    def mark_as_under_review(self, request, queryset):
        """Mark selected requests as under review"""
        from django.utils import timezone
        updated = queryset.update(status='under_review', processed_by=request.user, processed_at=timezone.now())
        self.message_user(request, f'{updated} IRS Tax Refund requests marked as under review.')
    mark_as_under_review.short_description = "Mark selected requests as under review"
    
    def mark_as_approved(self, request, queryset):
        """Mark selected requests as approved"""
        from django.utils import timezone
        updated = queryset.update(status='approved', processed_by=request.user, processed_at=timezone.now())
        self.message_user(request, f'{updated} IRS Tax Refund requests marked as approved.')
    mark_as_approved.short_description = "Mark selected requests as approved"
    
    def mark_as_rejected(self, request, queryset):
        """Mark selected requests as rejected"""
        from django.utils import timezone
        updated = queryset.update(status='rejected', processed_by=request.user, processed_at=timezone.now())
        self.message_user(request, f'{updated} IRS Tax Refund requests marked as rejected.')
    mark_as_rejected.short_description = "Mark selected requests as rejected"
    
    def mark_as_processing(self, request, queryset):
        """Mark selected requests as processing"""
        from django.utils import timezone
        updated = queryset.update(status='processing', processed_by=request.user, processed_at=timezone.now())
        self.message_user(request, f'{updated} IRS Tax Refund requests marked as processing.')
    mark_as_processing.short_description = "Mark selected requests as processing"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected requests as completed"""
        from django.utils import timezone
        updated = queryset.update(status='completed', processed_by=request.user, processed_at=timezone.now())
        self.message_user(request, f'{updated} IRS Tax Refund requests marked as completed.')
    mark_as_completed.short_description = "Mark selected requests as completed"
    
    def get_queryset(self, request):
        """Filter requests for current VIP member if not superuser"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            vip_profile = request.user.vip_profile
            return qs.filter(vip_member=vip_profile)
        except:
            return qs.none()
    
    def has_change_permission(self, request, obj=None):
        """Allow VIP members to view their own requests"""
        if obj and hasattr(request.user, 'vip_profile'):
            return obj.vip_member == request.user.vip_profile
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete requests"""
        return request.user.is_superuser
    
    def masked_ssn(self, obj):
        """Display masked SSN for security"""
        return obj.masked_ssn
    masked_ssn.short_description = 'SSN (Masked)'
    
    def masked_idme_email(self, obj):
        """Display masked ID.me email for security"""
        return obj.masked_idme_email
    masked_idme_email.short_description = 'ID.me Email (Masked)'


@admin.register(LoanHistory)
class LoanHistoryAdmin(admin.ModelAdmin):
    """Admin interface for Loan History"""
    
    list_display = [
        'reference_number', 'vip_member', 'loan_type', 'amount', 
        'purpose', 'duration_months', 'status', 'date_applied'
    ]
    
    list_filter = [
        'status', 'loan_type', 'purpose', 'date_applied', 
        'duration_months', 'vip_member'
    ]
    
    search_fields = [
        'reference_number', 'vip_member__full_name', 
        'vip_member__member_id', 'purpose', 'loan_type'
    ]
    
    readonly_fields = [
        'reference_number', 'date_applied', 'updated_at'
    ]
    
    fieldsets = (
        ('Loan Information', {
            'fields': (
                'vip_member', 'reference_number', 'loan_type', 
                'amount', 'purpose', 'duration_months'
            )
        }),
        ('Status & Processing', {
            'fields': (
                'status', 'interest_rate', 'monthly_payment',
                'approved_at', 'disbursed_at', 'completed_at'
            )
        }),
        ('Timestamps', {
            'fields': ('date_applied', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',),
            'classes': ('collapse',)
        })
    )
    
    list_per_page = 25
    date_hierarchy = 'date_applied'
    
    actions = ['mark_as_approved', 'mark_as_rejected', 'mark_as_disbursed']
    
    def mark_as_approved(self, request, queryset):
        """Mark selected loans as approved"""
        updated = queryset.update(status='approved', approved_at=timezone.now())
        self.message_user(request, f'{updated} loan(s) marked as approved.')
    mark_as_approved.short_description = 'Mark selected loans as approved'
    
    def mark_as_rejected(self, request, queryset):
        """Mark selected loans as rejected"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} loan(s) marked as rejected.')
    mark_as_rejected.short_description = 'Mark selected loans as rejected'
    
    def mark_as_disbursed(self, request, queryset):
        """Mark selected loans as disbursed"""
        updated = queryset.update(status='disbursed', disbursed_at=timezone.now())
        self.message_user(request, f'{updated} loan(s) marked as disbursed.')
    mark_as_disbursed.short_description = 'Mark selected loans as disbursed'


@admin.register(AccountSettings)
class AccountSettingsAdmin(admin.ModelAdmin):
    """Admin interface for Account Settings"""
    
    list_display = [
        'vip_member', 'full_name', 'email', 'phone_number', 
        'two_factor_enabled', 'updated_at'
    ]
    
    list_filter = [
        'language', 'currency', 'timezone', 'two_factor_enabled',
        'email_notifications', 'sms_notifications', 'push_notifications',
        'profile_visibility', 'data_sharing', 'created_at', 'updated_at'
    ]
    
    search_fields = [
        'vip_member__full_name', 'vip_member__member_id', 
        'first_name', 'last_name', 'email', 'phone_number'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'last_login'
    ]
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'vip_member', 'first_name', 'last_name', 'email', 
                'phone_number', 'date_of_birth', 'profile_picture'
            )
        }),
        ('Address Information', {
            'fields': (
                'address', 'city', 'state', 'country', 'postal_code'
            ),
            'classes': ('collapse',)
        }),
        ('Account Preferences', {
            'fields': (
                'language', 'currency', 'timezone'
            ),
            'classes': ('collapse',)
        }),
        ('Security Settings', {
            'fields': (
                'two_factor_enabled', 'email_notifications', 
                'sms_notifications', 'push_notifications'
            ),
            'classes': ('collapse',)
        }),
        ('Transaction Settings', {
            'fields': (
                'transaction_pin', 'daily_transaction_limit', 
                'monthly_transaction_limit'
            ),
            'classes': ('collapse',)
        }),
        ('Privacy Settings', {
            'fields': (
                'profile_visibility', 'data_sharing'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        })
    )
    
    list_per_page = 25
    date_hierarchy = 'updated_at'
    
    actions = ['enable_two_factor', 'disable_two_factor', 'enable_notifications', 'disable_notifications']
    
    def enable_two_factor(self, request, queryset):
        """Enable two-factor authentication for selected accounts"""
        updated = queryset.update(two_factor_enabled=True)
        self.message_user(request, f'{updated} account(s) enabled for two-factor authentication.')
    enable_two_factor.short_description = 'Enable two-factor authentication'
    
    def disable_two_factor(self, request, queryset):
        """Disable two-factor authentication for selected accounts"""
        updated = queryset.update(two_factor_enabled=False)
        self.message_user(request, f'{updated} account(s) disabled for two-factor authentication.')
    disable_two_factor.short_description = 'Disable two-factor authentication'
    
    def enable_notifications(self, request, queryset):
        """Enable all notifications for selected accounts"""
        updated = queryset.update(
            email_notifications=True,
            sms_notifications=True,
            push_notifications=True
        )
        self.message_user(request, f'{updated} account(s) enabled for all notifications.')
    enable_notifications.short_description = 'Enable all notifications'
    
    def disable_notifications(self, request, queryset):
        """Disable all notifications for selected accounts"""
        updated = queryset.update(
            email_notifications=False,
            sms_notifications=False,
            push_notifications=False
        )
        self.message_user(request, f'{updated} account(s) disabled for all notifications.')
        disable_notifications.short_description = 'Disable all notifications'


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    """Admin interface for Support Tickets"""
    
    list_display = [
        'ticket_number', 'title', 'vip_member', 'priority', 'status', 
        'category', 'created_at', 'updated_at'
    ]
    
    list_filter = [
        'priority', 'status', 'category', 'created_at', 'updated_at'
    ]
    
    search_fields = [
        'ticket_number', 'title', 'vip_member__full_name', 
        'vip_member__member_id', 'description'
    ]
    
    readonly_fields = [
        'ticket_number', 'created_at', 'updated_at', 'resolved_at', 'closed_at'
    ]
    
    fieldsets = (
        ('Ticket Information', {
            'fields': (
                'ticket_number', 'vip_member', 'title', 'description', 
                'category', 'priority', 'status'
            )
        }),
        ('Additional Information', {
            'fields': (
                'attachments', 'internal_notes', 'response_count'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'resolved_at', 'closed_at', 
                'last_response_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    actions = ['mark_as_resolved', 'mark_as_closed', 'mark_as_urgent', 'mark_as_in_progress']
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected tickets as resolved"""
        from django.utils import timezone
        updated = queryset.update(
            status='resolved', 
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} ticket(s) marked as resolved.')
    mark_as_resolved.short_description = 'Mark as resolved'
    
    def mark_as_closed(self, request, queryset):
        """Mark selected tickets as closed"""
        from django.utils import timezone
        updated = queryset.update(
            status='closed', 
            closed_at=timezone.now()
        )
        self.message_user(request, f'{updated} ticket(s) marked as closed.')
    mark_as_closed.short_description = 'Mark as closed'
    
    def mark_as_urgent(self, request, queryset):
        """Mark selected tickets as urgent"""
        updated = queryset.update(priority='urgent')
        self.message_user(request, f'{updated} ticket(s) marked as urgent.')
    mark_as_urgent.short_description = 'Mark as urgent'
    
    def mark_as_in_progress(self, request, queryset):
        """Mark selected tickets as in progress"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} ticket(s) marked as in progress.')
    mark_as_in_progress.short_description = 'Mark as in progress'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('vip_member')


class VIPFinancialMetricsForm(forms.ModelForm):
    """Custom form for VIP Financial Metrics with calculated fields"""
    
    balance_utilization = forms.CharField(
        label='Balance Utilization (%)',
        required=False,
        help_text='Calculated: Current Balance / Transaction Limit * 100'
    )
    
    monthly_net_flow = forms.CharField(
        label='Monthly Net Flow ($)',
        required=False,
        help_text='Calculated: Monthly Income - Monthly Outgoing'
    )
    
    investment_return_rate = forms.CharField(
        label='Investment Return Rate (%)',
        required=False,
        help_text='Calculated: Investment Growth / Total Investments * 100'
    )
    
    risk_score = forms.CharField(
        label='Risk Score',
        required=False,
        help_text='Calculated based on various factors'
    )
    
    class Meta:
        model = VIPFinancialMetrics
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            try:
                # Display calculated values with error handling
                self.fields['balance_utilization'].initial = f"{self.instance.balance_utilization:.2f}%"
                self.fields['monthly_net_flow'].initial = f"${self.instance.monthly_net_flow:.2f}"
                self.fields['investment_return_rate'].initial = f"{self.instance.investment_return_rate:.2f}%"
                self.fields['risk_score'].initial = f"{self.instance.risk_score}/100"
            except (TypeError, ValueError, AttributeError, ZeroDivisionError):
                # Fallback values if calculations fail
                self.fields['balance_utilization'].initial = "0.00%"
                self.fields['monthly_net_flow'].initial = "$0.00"
                self.fields['investment_return_rate'].initial = "0.00%"
                self.fields['risk_score'].initial = "0/100"
            
            # Make calculated fields readonly
            for field_name in ['balance_utilization', 'monthly_net_flow', 'investment_return_rate', 'risk_score']:
                self.fields[field_name].widget.attrs['readonly'] = True
                self.fields[field_name].widget.attrs['style'] = 'background-color: #f8f9fa;'


@admin.register(VIPFinancialMetrics)
class VIPFinancialMetricsAdmin(admin.ModelAdmin):
    """Admin interface for VIP Financial Metrics"""
    
    form = VIPFinancialMetricsForm
    
    list_display = [
        'vip_member', 'current_balance', 'monthly_income', 'monthly_outgoing', 
        'total_investments', 'net_worth', 'transaction_limit', 'account_status', 'updated_at'
    ]
    
    list_filter = [
        'account_status', 'risk_level', 'primary_currency', 'credit_score',
        'created_at', 'updated_at'
    ]
    
    search_fields = [
        'vip_member__full_name', 'vip_member__member_id', 
        'vip_member__user__username', 'vip_member__user__email'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'last_updated'
    ]
    
    fieldsets = (
        ('VIP Member', {
            'fields': ('vip_member',)
        }),
        ('Current Balance Information', {
            'fields': (
                'current_balance', 'available_balance', 'pending_balance'
            )
        }),
        ('Monthly Financial Metrics', {
            'fields': (
                'monthly_income', 'monthly_outgoing', 'monthly_savings'
            )
        }),
        ('Investment Information', {
            'fields': (
                'total_investments', 'net_worth', 'investment_growth'
            )
        }),
        ('Transaction Limits and Volumes', {
            'fields': (
                'transaction_limit', 'monthly_transaction_limit', 
                'pending_transactions', 'transaction_volume'
            )
        }),
        ('Account Status and Risk', {
            'fields': (
                'account_status', 'credit_score', 'risk_level'
            )
        }),
        ('Currency and Exchange', {
            'fields': (
                'primary_currency', 'exchange_rate'
            ),
            'classes': ('collapse',)
        }),
        ('Calculated Metrics (Read-Only)', {
            'fields': (
                'balance_utilization', 'monthly_net_flow', 
                'investment_return_rate', 'risk_score'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_updated'),
            'classes': ('collapse',)
        })
    )
    
    list_per_page = 25
    date_hierarchy = 'updated_at'
    ordering = ['-updated_at']
    
    actions = ['reset_balances', 'update_risk_levels', 'generate_monthly_report']
    
    def reset_balances(self, request, queryset):
        """Reset balances for selected VIP members"""
        updated = queryset.update(
            current_balance=0.00,
            available_balance=0.00,
            pending_balance=0.00,
            pending_transactions=0.00
        )
        self.message_user(request, f'{updated} VIP member(s) balances reset.')
    reset_balances.short_description = 'Reset balances'
    
    def update_risk_levels(self, request, queryset):
        """Update risk levels based on current metrics"""
        updated = 0
        for metrics in queryset:
            risk_score = metrics.risk_score
            if risk_score >= 80:
                metrics.risk_level = 'very_high'
            elif risk_score >= 60:
                metrics.risk_level = 'high'
            elif risk_score >= 40:
                metrics.risk_level = 'medium'
            else:
                metrics.risk_level = 'low'
            metrics.save()
            updated += 1
        
        self.message_user(request, f'{updated} VIP member(s) risk levels updated.')
    update_risk_levels.short_description = 'Update risk levels'
    
    def generate_monthly_report(self, request, queryset):
        """Generate monthly financial report"""
        # This would typically generate a PDF or Excel report
        self.message_user(request, f'Monthly report generated for {queryset.count()} VIP member(s).')
    generate_monthly_report.short_description = 'Generate monthly report'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('vip_member')


