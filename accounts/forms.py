from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import StaffProfile


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
            # Create staff profile
            StaffProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone_number=self.cleaned_data['phone_number'],
                department=self.cleaned_data['department']
            )
        
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
