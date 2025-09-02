from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    InvestmentCategory, InvestmentItem, PriceHistory, 
    UserInvestment, InvestmentTransaction, InvestmentPortfolio,
    RealTimePriceFeed, RealTimePriceHistory, AutoInvestmentPlan,
    CurrencyConversion, CustomerCashoutRequest
)
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import path
from django.contrib import messages
from django.core.management import call_command


@admin.register(InvestmentCategory)
class InvestmentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_color_preview(self, obj):
        if obj.color:
            return format_html(
                '<div style="background-color: {}; width: 20px; height: 20px; border-radius: 3px; border: 1px solid #ccc;"></div>',
                obj.color
            )
        return '-'
    get_color_preview.short_description = 'Color'


from .forms import InvestmentItemAdmin

@admin.register(InvestmentItem)
class InvestmentItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'current_price_usd', 'symbol', 
        'investment_type', 'is_active', 'is_featured', 'created_at'
    ]
    list_filter = [
        'category', 'investment_type', 'is_active', 'is_featured', 
        'created_at', 'symbol'
    ]
    search_fields = ['name', 'description', 'symbol']
    ordering = ['name']
    list_editable = ['is_active', 'is_featured', 'symbol']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'investment_type')
        }),
        ('Pricing', {
            'fields': ('current_price_usd', 'minimum_investment', 'symbol')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['item', 'price', 'change_amount', 'change_percentage', 'timestamp']
    list_filter = ['timestamp', 'item__category']
    search_fields = ['item__name']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    def get_change_amount_display(self, obj):
        if obj.change_amount > 0:
            return format_html(
                '<span style="color: green;">+${}</span>',
                obj.change_amount
            )
        elif obj.change_amount < 0:
            return format_html(
                '<span style="color: red;">-${}</span>',
                abs(obj.change_amount)
            )
        return '$0.00'
    get_change_amount_display.short_description = 'Change Amount'


@admin.register(UserInvestment)
class UserInvestmentAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'item', 'investment_amount_usd', 'current_value_usd', 
        'total_return_usd', 'total_return_percentage', 'investment_type', 'status'
    ]
    list_filter = [
        'investment_type', 'status', 'purchased_at', 'item__category'
    ]
    search_fields = ['user__username', 'user__email', 'item__name']
    ordering = ['-purchased_at']
    readonly_fields = ['purchased_at', 'updated_at', 'current_value_usd', 'total_return_usd', 'total_return_percentage']
    
    fieldsets = (
        ('User & Item', {
            'fields': ('user', 'item')
        }),
        ('Investment Details', {
            'fields': ('investment_amount_usd', 'quantity', 'purchase_price_per_unit')
        }),
        ('Current Status', {
            'fields': ('current_value_usd', 'total_return_usd', 'total_return_percentage')
        }),
        ('Investment Type', {
            'fields': ('investment_type', 'status')
        }),
        ('Timestamps', {
            'fields': ('purchased_at', 'updated_at', 'sold_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_return_display(self, obj):
        if obj.total_return_usd > 0:
            return format_html(
                '<span style="color: green;">+${}</span>',
                obj.total_return_usd
            )
        elif obj.total_return_usd < 0:
            return format_html(
                '<span style="color: red;">-${}</span>',
                abs(obj.total_return_usd)
            )
        return '$0.00'
    get_total_return_display.short_description = 'Total Return'


@admin.register(InvestmentTransaction)
class InvestmentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'user', 'item', 'transaction_type', 'amount_usd', 
        'payment_status', 'created_at'
    ]
    list_filter = [
        'transaction_type', 'payment_status', 'payment_method', 'created_at'
    ]
    search_fields = [
        'transaction_id', 'user__username', 'user__email', 'item__name'
    ]
    ordering = ['-created_at']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('transaction_id', 'user', 'investment', 'item')
        }),
        ('Transaction Details', {
            'fields': ('transaction_type', 'amount_usd', 'quantity', 'price_per_unit')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_reference', 'payment_status')
        }),
        ('NOWPayments', {
            'fields': (
                'nowpayments_payment_id', 'nowpayments_payment_status',
                'crypto_amount', 'crypto_currency'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('description', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InvestmentPortfolio)
class InvestmentPortfolioAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'total_invested', 'current_value', 'total_return', 
        'total_return_percentage', 'active_investments_count', 'last_updated'
    ]
    list_filter = ['last_updated']
    search_fields = ['user__username', 'user__email']
    ordering = ['-last_updated']
    readonly_fields = ['last_updated']
    
    def get_total_return_display(self, obj):
        if obj.total_return > 0:
            return format_html(
                '<span style="color: green;">+${}</span>',
                obj.total_return
            )
        elif obj.total_return < 0:
            return format_html(
                '<span style="color: red;">-${}</span>',
                abs(obj.total_return)
            )
        return '$0.00'
    get_total_return_display.short_description = 'Total Return'
    
    def get_total_return_percentage_display(self, obj):
        if obj.total_return_percentage > 0:
            return format_html(
                '<span style="color: green;">+{}%</span>',
                obj.total_return_percentage
            )
        elif obj.total_return_percentage < 0:
            return format_html(
                '<span style="color: red;">-{}%</span>',
                abs(obj.total_return_percentage)
            )
        return '0.00%'
    get_total_return_percentage_display.short_description = 'Total Return %'


@admin.register(RealTimePriceFeed)
class RealTimePriceFeedAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'symbol', 'asset_type', 'current_price', 
        'price_change_24h', 'price_change_percentage_24h', 
        'is_active', 'last_updated'
    ]
    list_filter = ['asset_type', 'is_active', 'api_source', 'last_updated']
    search_fields = ['name', 'symbol']
    ordering = ['name']
    list_editable = ['is_active', 'current_price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'symbol', 'asset_type', 'api_source')
        }),
        ('Pricing', {
            'fields': ('current_price', 'price_change_24h', 'price_change_percentage_24h')
        }),
        ('API Configuration', {
            'fields': ('api_url', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ['last_updated']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fix-production-db/', self.admin_site.admin_view(self.fix_production_db), name='fix-production-db'),
        ]
        return custom_urls + urls

    def fix_production_db(self, request):
        """Fix production database issues"""
        try:
            # Call the management command
            call_command('fix_production_db', verbosity=0)
            messages.success(request, '✅ Production database fixed successfully! Live price updates should now work.')
        except Exception as e:
            messages.error(request, f'❌ Error fixing production database: {str(e)}')
        
        return HttpResponseRedirect('../')

# Add custom admin actions
@admin.action(description="Fix production database issues")
def fix_production_database(modeladmin, request, queryset):
    """Admin action to fix production database"""
    try:
        call_command('fix_production_db', verbosity=0)
        messages.success(request, '✅ Production database fixed successfully! Live price updates should now work.')
    except Exception as e:
        messages.error(request, f'❌ Error fixing production database: {str(e)}')

# Add the action to InvestmentItem admin
InvestmentItemAdmin.actions = [fix_production_database]

# Add the action to RealTimePriceFeed admin  
RealTimePriceFeedAdmin.actions = [fix_production_database]


@admin.register(RealTimePriceHistory)
class RealTimePriceHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'price_feed', 'price', 'change_amount', 'change_percentage', 'timestamp'
    ]
    list_filter = ['price_feed__asset_type', 'timestamp']
    search_fields = ['price_feed__name']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']


@admin.register(AutoInvestmentPlan)
class AutoInvestmentPlanAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'name', 'target_asset', 'investment_amount', 'frequency',
        'status', 'next_investment_date', 'total_invested', 'investments_count'
    ]
    list_filter = ['status', 'frequency', 'target_asset__category', 'created_at']
    search_fields = ['user__username', 'user__email', 'name', 'target_asset__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_investment_at']
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('user', 'name', 'description', 'target_asset')
        }),
        ('Investment Details', {
            'fields': ('investment_amount', 'frequency')
        }),
        ('Schedule', {
            'fields': ('start_date', 'next_investment_date', 'end_date')
        }),
        ('Status', {
            'fields': ('status', 'total_invested', 'investments_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_investment_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CurrencyConversion)
class CurrencyConversionAdmin(admin.ModelAdmin):
    list_display = [
        'from_currency', 'to_currency', 'exchange_rate', 'api_source', 'last_updated'
    ]
    list_filter = ['from_currency', 'to_currency', 'last_updated']
    search_fields = ['from_currency', 'to_currency']
    ordering = ['from_currency', 'to_currency']
    readonly_fields = ['last_updated']


@admin.register(CustomerCashoutRequest)
class CustomerCashoutRequestAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'amount_usd', 'requested_currency', 'status', 'approved_by', 'created_at'
    ]
    list_filter = ['status', 'requested_currency', 'created_at', 'approved_at']
    search_fields = ['user__username', 'user__email', 'bank_account_details']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'amount_usd', 'requested_currency', 'bank_account_details', 'reason')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'approved_by')
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            if obj.status == 'approved' and not obj.approved_by:
                obj.approved_by = request.user
                obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)
