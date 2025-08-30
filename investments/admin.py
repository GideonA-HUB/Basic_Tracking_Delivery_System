from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    InvestmentCategory, InvestmentItem, PriceHistory, 
    UserInvestment, InvestmentTransaction, InvestmentPortfolio
)


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


@admin.register(InvestmentItem)
class InvestmentItemAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'current_price_usd', 'price_change_24h', 
        'price_change_percentage_24h', 'investment_type', 'is_active', 'is_featured'
    ]
    list_filter = [
        'category', 'investment_type', 'is_active', 'is_featured', 
        'created_at', 'updated_at'
    ]
    search_fields = ['name', 'description', 'category__name']
    ordering = ['-is_featured', '-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('current_price_usd', 'price_change_24h', 'price_change_percentage_24h')
        }),
        ('Specifications', {
            'fields': ('weight', 'purity', 'dimensions', 'origin')
        }),
        ('Investment Options', {
            'fields': ('investment_type', 'minimum_investment', 'maximum_investment')
        }),
        ('Availability', {
            'fields': ('total_available', 'currently_available')
        }),
        ('Media', {
            'fields': ('main_image', 'additional_images')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_price_change_display(self, obj):
        if obj.price_change_24h > 0:
            return format_html(
                '<span style="color: green;">+${}</span>',
                obj.price_change_24h
            )
        elif obj.price_change_24h < 0:
            return format_html(
                '<span style="color: red;">-${}</span>',
                abs(obj.price_change_24h)
            )
        return '$0.00'
    get_price_change_display.short_description = '24h Change'
    
    def get_percentage_change_display(self, obj):
        if obj.price_change_percentage_24h > 0:
            return format_html(
                '<span style="color: green;">+{}%</span>',
                obj.price_change_percentage_24h
            )
        elif obj.price_change_percentage_24h < 0:
            return format_html(
                '<span style="color: red;">-{}%</span>',
                abs(obj.price_change_percentage_24h)
            )
        return '0.00%'
    get_percentage_change_display.short_description = '24h % Change'


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
