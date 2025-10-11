from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import StaffProfile, CustomerProfile


class CustomerRegistrationForm(UserCreationForm):
    """Form for customer registration"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    country = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = False  # Ensure they are not staff
        
        if commit:
            user.save()
            # Get or create customer profile to avoid duplicate key errors
            customer_profile, created = CustomerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': self.cleaned_data['phone_number'],
                    'address': self.cleaned_data['address'],
                    'city': self.cleaned_data['city'],
                    'state': self.cleaned_data['state'],
                    'country': self.cleaned_data['country'],
                    'postal_code': self.cleaned_data['postal_code'],
                    'date_of_birth': self.cleaned_data['date_of_birth']
                }
            )
            
            # If profile already existed, update it with form data
            if not created:
                customer_profile.phone_number = self.cleaned_data['phone_number']
                customer_profile.address = self.cleaned_data['address']
                customer_profile.city = self.cleaned_data['city']
                customer_profile.state = self.cleaned_data['state']
                customer_profile.country = self.cleaned_data['country']
                customer_profile.postal_code = self.cleaned_data['postal_code']
                customer_profile.date_of_birth = self.cleaned_data['date_of_birth']
                customer_profile.save()
        
        return user


class CustomerLoginForm(AuthenticationForm):
    """Custom login form for customers"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            try:
                user = User.objects.get(username=username)
                if user.is_staff:
                    raise forms.ValidationError("This login is for customers only. Staff members should use the staff login.")
            except User.DoesNotExist:
                # Try to find by email
                try:
                    user = User.objects.get(email=username)
                    if user.is_staff:
                        raise forms.ValidationError("This login is for customers only. Staff members should use the staff login.")
                except User.DoesNotExist:
                    pass
        
        return cleaned_data


class StaffRegistrationForm(UserCreationForm):
    """Form for staff registration"""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    department = forms.CharField(max_length=100, required=False)
    role = forms.ChoiceField(choices=StaffProfile.ROLE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = True  # Make them staff by default
        
        if commit:
            user.save()
            # Get or create staff profile to avoid duplicate key errors
            staff_profile, created = StaffProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': self.cleaned_data['role'],
                    'phone_number': self.cleaned_data['phone_number'],
                    'department': self.cleaned_data['department']
                }
            )
            
            # If profile already existed, update it with form data
            if not created:
                staff_profile.role = self.cleaned_data['role']
                staff_profile.phone_number = self.cleaned_data['phone_number']
                staff_profile.department = self.cleaned_data['department']
                staff_profile.save()
        
        return user


class StaffLoginForm(AuthenticationForm):
    """Custom login form for staff"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            try:
                user = User.objects.get(username=username)
                if not user.is_staff:
                    raise forms.ValidationError("Access denied. Only staff members can log in.")
            except User.DoesNotExist:
                pass
        
        return cleaned_data


class VIPLoginForm(AuthenticationForm):
    """Custom login form for VIP members"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500',
            'placeholder': 'VIP Username or Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500',
            'placeholder': 'VIP Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            try:
                user = User.objects.get(username=username)
                # For now, allow any authenticated user to access VIP
                # In production, you would check for VIP status here
                if not user.is_active:
                    raise forms.ValidationError("Account is not active.")
            except User.DoesNotExist:
                # Try to find by email
                try:
                    user = User.objects.get(email=username)
                    if not user.is_active:
                        raise forms.ValidationError("Account is not active.")
                except User.DoesNotExist:
                    pass
        
        return cleaned_data