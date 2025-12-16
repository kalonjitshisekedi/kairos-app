"""
Forms for core app with POPIA compliance.
"""
from django import forms
from django.core.validators import FileExtensionValidator
from .models import ContactInquiry


class ContactInquiryForm(forms.ModelForm):
    popia_consent = forms.BooleanField(
        required=True,
        error_messages={
            'required': 'You must consent to POPIA processing to submit this form.'
        }
    )
    
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'company', 'inquiry_type', 'message', 'popia_consent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'inquiry_type': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tell us about your project, the expertise you\'re looking for, or any questions you have...',
                'required': True
            }),
        }
    
    def clean_popia_consent(self):
        consent = self.cleaned_data.get('popia_consent')
        if not consent:
            raise forms.ValidationError(
                'You must consent to POPIA processing to submit this form. '
                'Your data will be processed in accordance with the Protection of Personal Information Act.'
            )
        return consent
