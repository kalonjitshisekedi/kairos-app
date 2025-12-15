"""
Forms for user authentication and registration.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm

User = get_user_model()


class SignUpForm(UserCreationForm):
    ROLE_CHOICES = [
        ('client', 'I need expert consultation'),
        ('expert', 'I am an expert'),
    ]

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )
    privacy_consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I agree to the privacy policy and consent to the processing of my personal data'
    )
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I accept the terms of service and acceptable use policy'
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'password1', 'password2', 'privacy_consent', 'terms_accepted']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.privacy_consent = self.cleaned_data['privacy_consent']
        user.terms_accepted = self.cleaned_data['terms_accepted']
        if self.cleaned_data['privacy_consent']:
            from django.utils import timezone
            user.privacy_consent_date = timezone.now()
        if self.cleaned_data['terms_accepted']:
            from django.utils import timezone
            user.terms_accepted_date = timezone.now()
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DeletionRequestForm(forms.Form):
    confirm_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email to confirm'}),
        label='Confirm your email address'
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional: Tell us why you are leaving'}),
        label='Reason for deletion (optional)'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_confirm_email(self):
        email = self.cleaned_data['confirm_email']
        if email != self.user.email:
            raise forms.ValidationError('Email does not match your account email.')
        return email
