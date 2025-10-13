from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Card, StaffProfile, CustomerProfile, VIPProfile, LocalTransfer, InternationalTransfer


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


class InternationalTransferForm(forms.ModelForm):
    """Form for international transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_amount', 'currency', 'transfer_method', 'recipient_name', 
            'recipient_email', 'recipient_phone', 'bank_name', 'bank_address',
            'account_number', 'routing_number', 'swift_code', 'iban',
            'wallet_address', 'wallet_type', 'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'transfer_method': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipient\'s full name'
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipient\'s email address'
            }),
            'recipient_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipient\'s phone number (optional)'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bank name'
            }),
            'bank_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter bank address'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account number'
            }),
            'routing_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter routing number'
            }),
            'swift_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter SWIFT/BIC code'
            }),
            'iban': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter IBAN'
            }),
            'wallet_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter wallet address'
            }),
            'wallet_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter wallet type (e.g., Bitcoin, Ethereum)'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter additional description (optional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set choices for form fields
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['transfer_method'].choices = InternationalTransfer.TRANSFER_METHOD_CHOICES
        
        # Set initial values
        self.fields['currency'].initial = 'USD'
        
        # Make some fields optional
        self.fields['recipient_phone'].required = False
        self.fields['bank_name'].required = False
        self.fields['bank_address'].required = False
        self.fields['account_number'].required = False
        self.fields['routing_number'].required = False
        self.fields['swift_code'].required = False
        self.fields['iban'].required = False
        self.fields['wallet_address'].required = False
        self.fields['wallet_type'].required = False
        self.fields['description'].required = False
    
    def clean_transfer_amount(self):
        """Validate transfer amount"""
        amount = self.cleaned_data.get('transfer_amount')
        if amount:
            if amount <= 0:
                raise forms.ValidationError('Transfer amount must be greater than $0.00')
            if amount > 100000:
                raise forms.ValidationError('Transfer amount cannot exceed $100,000.00')
        return amount
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        transfer_method = cleaned_data.get('transfer_method')
        
        # Validate based on transfer method
        if transfer_method == 'wire_transfer':
            if not cleaned_data.get('bank_name'):
                raise forms.ValidationError('Bank name is required for wire transfers')
            if not cleaned_data.get('account_number'):
                raise forms.ValidationError('Account number is required for wire transfers')
        elif transfer_method == 'cryptocurrency':
            if not cleaned_data.get('wallet_address'):
                raise forms.ValidationError('Wallet address is required for cryptocurrency transfers')
            if not cleaned_data.get('wallet_type'):
                raise forms.ValidationError('Wallet type is required for cryptocurrency transfers')
        
        return cleaned_data


# Specific forms for each transfer method
class WireTransferForm(forms.ModelForm):
    """Form for Wire Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 'recipient_email',
            'bank_name', 'bank_address', 'account_number', 'routing_number',
            'swift_code', 'iban', 'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter beneficiary\'s full name'
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter beneficiary\'s email address'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bank name'
            }),
            'bank_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter bank address'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account number'
            }),
            'routing_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter routing number'
            }),
            'swift_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter SWIFT/BIC code'
            }),
            'iban': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter IBAN number'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'wire_transfer'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False


class CryptocurrencyForm(forms.ModelForm):
    """Form for Cryptocurrency Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 'recipient_email',
            'wallet_address', 'wallet_type', 'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipient\'s full name'
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipient\'s email address'
            }),
            'wallet_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter wallet address'
            }),
            'wallet_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter wallet type (e.g., Bitcoin, Ethereum)'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'cryptocurrency'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False


class PayPalForm(forms.ModelForm):
    """Form for PayPal Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_email', 'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter PayPal email address'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'paypal'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False


class WiseTransferForm(forms.ModelForm):
    """Form for Wise Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 'recipient_email',
            'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'wise_transfer'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False


class CashAppForm(forms.ModelForm):
    """Form for Cash App Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'cash_app'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False


class SkrillForm(forms.ModelForm):
    """Form for Skrill Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 'recipient_email',
            'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Skrill email address'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'skrill'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False


class VenmoForm(forms.ModelForm):
    """Form for Venmo Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 'recipient_phone',
            'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'recipient_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number associated with Venmo'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'venmo'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False


class ZelleForm(forms.ModelForm):
    """Form for Zelle Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 'recipient_email',
            'recipient_phone', 'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Zelle email address'
            }),
            'recipient_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number associated with Zelle'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'zelle'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False


class RevolutForm(forms.ModelForm):
    """Form for Revolut Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 'recipient_email',
            'recipient_phone', 'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'recipient_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number associated with Revolut'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'revolut'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False


class AlipayForm(forms.ModelForm):
    """Form for Alipay Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'alipay'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False


class WeChatPayForm(forms.ModelForm):
    """Form for WeChat Pay Transfer"""
    
    class Meta:
        model = InternationalTransfer
        fields = [
            'transfer_method', 'transfer_amount', 'currency', 'recipient_name', 'purpose_of_transfer', 'description'
        ]
        widgets = {
            'transfer_method': forms.HiddenInput(),  # Hidden field since it's set automatically
            'transfer_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'purpose_of_transfer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter purpose of transfer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional payment description or note'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_method'].initial = 'wechat_pay'
        self.fields['currency'].choices = InternationalTransfer.CURRENCY_CHOICES
        self.fields['description'].required = False