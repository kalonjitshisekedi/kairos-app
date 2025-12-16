"""
Expert application form with POPIA compliance and secure file upload.
"""
from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .models import ExpertApplication


def validate_file_size(file):
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        raise ValidationError(f'File size must be under 10MB. Your file is {file.size / (1024*1024):.1f}MB.')


class ExpertApplicationForm(forms.ModelForm):
    cv_file = forms.FileField(
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx']),
            validate_file_size
        ],
        help_text='Upload your CV in PDF, DOC, or DOCX format (max 10MB)'
    )
    
    popia_consent = forms.BooleanField(
        required=True,
        error_messages={
            'required': 'You must consent to POPIA processing to submit this application.'
        }
    )
    
    years_experience = forms.ChoiceField(
        choices=[
            ('0', 'Select...'),
            ('3', '3-5 years'),
            ('5', '5-10 years'),
            ('10', '10-15 years'),
            ('15', '15-20 years'),
            ('20', '20+ years'),
        ],
        required=False
    )
    
    class Meta:
        model = ExpertApplication
        fields = [
            'full_name', 'email', 'phone', 'linkedin_url', 'github_url',
            'orcid_id', 'expertise_areas', 'years_experience', 'bio',
            'cv_file', 'popia_consent'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+27...'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/...'}),
            'orcid_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000-0000-0000-0000'}),
            'expertise_areas': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Machine Learning, Financial Analysis, Strategic Consulting',
                'required': True
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about your background, achievements, and what makes you an expert in your field...'
            }),
        }
    
    def clean_popia_consent(self):
        consent = self.cleaned_data.get('popia_consent')
        if not consent:
            raise forms.ValidationError(
                'You must consent to POPIA processing to submit this application. '
                'Your CV and application details will be reviewed by the Kairos team in accordance with POPIA.'
            )
        return consent
    
    def clean_cv_file(self):
        cv_file = self.cleaned_data.get('cv_file')
        if cv_file:
            content_type = cv_file.content_type
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            if content_type not in allowed_types:
                raise ValidationError('Only PDF, DOC, and DOCX files are allowed.')
        return cv_file
    
    def clean_years_experience(self):
        years = self.cleaned_data.get('years_experience', '0')
        return int(years) if years else 0
