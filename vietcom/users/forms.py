from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    full_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'phone', 'gender', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes and placeholders to all fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '✨ Nhập tên đăng nhập của bạn'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '🔒 Tạo mật khẩu mạnh'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '🔒 Nhập lại mật khẩu'
        })
        
        # Update other field placeholders
        self.fields['email'].widget.attrs.update({
            'placeholder': '📧 Email của bạn (ví dụ: yourname@gmail.com)'
        })
        self.fields['full_name'].widget.attrs.update({
            'placeholder': '👤 Họ và tên đầy đủ của bạn'
        })
        self.fields['phone'].widget.attrs.update({
            'placeholder': '📱 Số điện thoại (ví dụ: 0901234567)'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("A user with this phone number already exists.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.phone = self.cleaned_data['phone']
        user.gender = self.cleaned_data.get('gender')
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Custom user edit form"""
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'phone', 'hometown', 'date_of_birth', 
                 'gender', 'bio', 'avatar', 'interests')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'hometown': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Tell us about yourself (max 500 characters)'
            }),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'interests': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter interests separated by commas'
            }),
        }


class LoginForm(forms.Form):
    """Custom login form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '💌 Email hoặc tên đăng nhập'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '🔐 Mật khẩu của bạn'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
                if not user:
                    raise ValidationError("Invalid email or password.")
                if not user.is_active:
                    raise ValidationError("This account is inactive.")
            except User.DoesNotExist:
                raise ValidationError("Invalid email or password.")

        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User
        # Đổi 'dob' thành 'date_of_birth'
        fields = ['full_name', 'hometown', 'date_of_birth', 'gender', 'bio', 'avatar', 'search_radius']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'hometown': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your hometown'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself (max 500 characters)'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'search_radius': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '500',
                'step': '0.1'
            }),
        }

    def clean_search_radius(self):
        radius = self.cleaned_data.get('search_radius')
        if radius and (radius < 1 or radius > 500):
            raise ValidationError("Search radius must be between 1 and 500 km.")
        return radius


class PasswordChangeForm(forms.Form):
    """Custom password change form"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current password'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("Your current password is incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError("The new passwords don't match.")
            if len(new_password1) < 8:
                raise ValidationError("Password must be at least 8 characters long.")

        return cleaned_data

    def save(self):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


class UserSearchForm(forms.Form):
    """Form for searching users"""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, username, or email'
        })
    )
    gender = forms.ChoiceField(
        choices=[('', 'All')] + User.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All')] + User.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    min_level = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min level',
            'min': '1'
        })
    )
    max_level = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max level',
            'min': '1'
        })
    )