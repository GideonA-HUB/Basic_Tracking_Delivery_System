from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Card, StaffProfile, CustomerProfile, VIPProfile, LocalTransfer


class StaffLoginForm(AuthenticationForm):
    """Staff login form"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class StaffRegistrationForm(UserCreationForm):
    """Staff registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = False
        if commit:
            user.save()
            StaffProfile.objects.create(user=user)
        return user


class CustomerRegistrationForm(UserCreationForm):
    """Customer registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        if commit:
            user.save()
            CustomerProfile.objects.create(user=user)
        return user


class CustomerLoginForm(AuthenticationForm):
    """Customer login form"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class VIPLoginForm(AuthenticationForm):
    """VIP login form"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class CardApplicationForm(forms.ModelForm):
    """Form for card application"""
    
    class Meta:
        model = Card
        fields = [
            'card_brand', 'card_level', 'currency', 'daily_spending_limit',
            'cardholder_name', 'billing_address', 'terms_accepted'
        ]
        widgets = {
            'card_brand': forms.RadioSelect(attrs={'class': 'card-brand-radio'}),
            'card_level': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'daily_spending_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1000',
                'max': '10000',
                'step': '100'
            }),
            'cardholder_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'billing_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your billing address'
            }),
            'terms_accepted': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set choices for form fields
        self.fields['card_brand'].choices = Card.CARD_BRAND_CHOICES
        self.fields['card_level'].choices = [('', 'Select a card level')] + Card.CARD_LEVEL_CHOICES
        self.fields['currency'].choices = Card.CURRENCY_CHOICES
        
        # Set initial values
        self.fields['daily_spending_limit'].initial = 1000
        self.fields['currency'].initial = 'USD'
        
        # Add help text
        self.fields['daily_spending_limit'].help_text = 'Limits: $1,000.00 - $10,000.00'
        self.fields['cardholder_name'].help_text = 'Name as it will appear on your card'
        self.fields['billing_address'].help_text = 'Address used for verification when making purchases'
    
    def clean_daily_spending_limit(self):
        """Validate daily spending limit"""
        limit = self.cleaned_data.get('daily_spending_limit')
        if limit:
            if limit < 1000:
                raise forms.ValidationError('Daily spending limit must be at least $1,000.00')
            if limit > 10000:
                raise forms.ValidationError('Daily spending limit cannot exceed $10,000.00')
        return limit
    
    def clean_terms_accepted(self):
        """Validate terms acceptance"""
        terms = self.cleaned_data.get('terms_accepted')
        if not terms:
            raise forms.ValidationError('You must accept the terms and conditions to apply for a card.')
        return terms


class LocalTransferForm(forms.ModelForm):
    """Form for local transfer"""
    
    class Meta:
        model = LocalTransfer
        fields = [
            'transfer_amount', 'currency', 'beneficiary_name', 
            'beneficiary_account_number', 'bank_name', 'transfer_type', 'description'
        ]
        widgets = {
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'beneficiary_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter beneficiary\'s full name'
            }),
            'beneficiary_account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account number'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bank name'
            }),
            'transfer_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter transaction description or purpose of payment'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set choices for form fields
        self.fields['currency'].choices = LocalTransfer.CURRENCY_CHOICES
        self.fields['transfer_type'].choices = LocalTransfer.TRANSFER_TYPE_CHOICES
        
        # Set initial values
        self.fields['currency'].initial = 'USD'
        self.fields['transfer_type'].initial = 'online_banking'
    
    def clean_transfer_amount(self):
        """Validate transfer amount"""
        amount = self.cleaned_data.get('transfer_amount')
        if amount:
            if amount <= 0:
                raise forms.ValidationError('Transfer amount must be greater than $0.00')
            if amount > 50000:
                raise forms.ValidationError('Transfer amount cannot exceed $50,000.00')
        return amount
    
    def clean_beneficiary_account_number(self):
        """Validate account number"""
        account_number = self.cleaned_data.get('beneficiary_account_number')
        if account_number:
            # Remove any spaces or dashes
            account_number = account_number.replace(' ', '').replace('-', '')
            if not account_number.isdigit():
                raise forms.ValidationError('Account number must contain only digits')
            if len(account_number) < 8:
                raise forms.ValidationError('Account number must be at least 8 digits long')
        return account_number