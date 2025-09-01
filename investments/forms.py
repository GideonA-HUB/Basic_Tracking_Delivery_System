from django import forms
from django.contrib import admin
from .models import InvestmentItem
import json
from django.utils.html import format_html


class InvestmentItemAdminForm(forms.ModelForm):
    """Custom form for InvestmentItem admin with better URL handling"""
    
    additional_image_urls_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'cols': 80,
            'placeholder': 'Enter image URLs, one per line or separated by commas\nExample:\nhttps://example.com/image1.jpg\nhttps://example.com/image2.jpg'
        }),
        required=False,
        help_text="Enter image URLs, one per line or separated by commas"
    )
    
    class Meta:
        model = InvestmentItem
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Convert JSON list to text for editing
            if self.instance.additional_image_urls:
                if isinstance(self.instance.additional_image_urls, list):
                    self.fields['additional_image_urls_text'].initial = '\n'.join(self.instance.additional_image_urls)
                else:
                    self.fields['additional_image_urls_text'].initial = str(self.instance.additional_image_urls)
    
    def clean_additional_image_urls_text(self):
        """Convert text input to JSON list"""
        text = self.cleaned_data.get('additional_image_urls_text', '')
        if not text:
            return []
        
        # Split by newlines and commas, then clean up
        urls = []
        for line in text.split('\n'):
            for url in line.split(','):
                url = url.strip()
                if url:
                    urls.append(url)
        
        return urls
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Convert text to JSON list
        instance.additional_image_urls = self.cleaned_data.get('additional_image_urls_text', [])
        if commit:
            instance.save()
        return instance


class InvestmentItemAdmin(admin.ModelAdmin):
    form = InvestmentItemAdminForm
    
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
            'fields': ('main_image_url', 'additional_image_urls_text'),
            'description': 'Enter image URLs instead of uploading files. For additional images, enter URLs separated by commas or one per line.'
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


# Admin registration is handled in admin.py
