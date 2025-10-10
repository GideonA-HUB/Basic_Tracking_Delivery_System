from django import forms
from .models import VIPApplication
from decimal import Decimal


class VIPApplicationForm(forms.ModelForm):
    """Form for VIP membership applications"""
    
    # Custom field for net worth range
    NET_WORTH_CHOICES = [
        ('', 'Select Net Worth Range'),
        ('Under $50,000', 'Under $50,000'),
        ('$50,000 - $100,000', '$50,000 - $100,000'),
        ('$100,000 - $250,000', '$100,000 - $250,000'),
        ('$250,000 - $500,000', '$250,000 - $500,000'),
        ('$500,000 - $1,000,000', '$500,000 - $1,000,000'),
        ('$1,000,000 - $5,000,000', '$1,000,000 - $5,000,000'),
        ('Over $5,000,000', 'Over $5,000,000'),
    ]
    
    net_worth_range = forms.ChoiceField(
        choices=NET_WORTH_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        help_text="Please select your estimated net worth range"
    )
    
    expected_monthly_investment = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'step': '0.01',
            'placeholder': '0.00'
        }),
        help_text="How much do you expect to invest monthly?"
    )
    
    reason_for_application = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell us why you want to become a VIP member...'
        }),
        help_text="Please explain why you want to become a VIP member"
    )
    
    investment_experience = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe your investment experience and background...'
        }),
        help_text="Please describe your investment experience"
    )
    
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567'
        }),
        help_text="Phone number (optional but recommended for faster approval)"
    )
    
    class Meta:
        model = VIPApplication
        fields = [
            'requested_tier',
            'reason_for_application',
            'investment_experience',
            'expected_monthly_investment',
            'net_worth_range',
            'phone',
            'preferred_contact_method'
        ]
        widgets = {
            'requested_tier': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'preferred_contact_method': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def clean_expected_monthly_investment(self):
        amount = self.cleaned_data.get('expected_monthly_investment')
        if amount and amount < Decimal('100.00'):
            raise forms.ValidationError("Minimum expected monthly investment is $100.00")
        return amount
    
    def clean_reason_for_application(self):
        reason = self.cleaned_data.get('reason_for_application')
        if reason and len(reason.strip()) < 50:
            raise forms.ValidationError("Please provide a more detailed reason (at least 50 characters)")
        return reason
    
    def clean_investment_experience(self):
        experience = self.cleaned_data.get('investment_experience')
        if experience and len(experience.strip()) < 30:
            raise forms.ValidationError("Please provide more details about your investment experience (at least 30 characters)")
        return experience
