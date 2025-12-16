"""
Forms for expert profile management.
"""
from django import forms
from .models import ExpertProfile, Publication, Patent, NotableProject, VerificationDocument, ExpertiseTag


class ExpertProfileBasicForm(forms.ModelForm):
    class Meta:
        model = ExpertProfile
        fields = ['headline', 'bio', 'pronouns', 'affiliation', 'location', 'timezone']
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Machine learning researcher specialising in NLP'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Tell potential clients about your expertise, experience, and what makes you unique'}),
            'pronouns': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. she/her, he/him, they/them'}),
            'affiliation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. University of Oxford'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. London, UK'}),
            'timezone': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import pytz
        self.fields['timezone'].widget.choices = [(tz, tz) for tz in pytz.common_timezones]


class ExpertProfileAvatarForm(forms.ModelForm):
    class Meta:
        model = ExpertProfile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class ExpertProfileExpertiseForm(forms.ModelForm):
    expertise_tags = forms.ModelMultipleChoiceField(
        queryset=ExpertiseTag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    languages = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. English, French, German'}),
        required=False,
        help_text='Comma-separated list of languages you speak'
    )

    class Meta:
        model = ExpertProfile
        fields = ['expertise_tags', 'orcid_id']
        widgets = {
            'orcid_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 0000-0002-1234-5678'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance and instance.languages:
            self.fields['languages'].initial = ', '.join(instance.languages)

    def save(self, commit=True):
        instance = super().save(commit=False)
        languages_str = self.cleaned_data.get('languages', '')
        instance.languages = [lang.strip() for lang in languages_str.split(',') if lang.strip()]
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ExpertProfileExperienceForm(forms.ModelForm):
    class Meta:
        model = ExpertProfile
        fields = ['years_experience', 'senior_roles', 'sector_expertise', 'privacy_level', 'project_work_available']
        widgets = {
            'years_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'senior_roles': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List senior positions you have held'}),
            'sector_expertise': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your industry sectors of expertise'}),
            'privacy_level': forms.Select(attrs={'class': 'form-select'}),
            'project_work_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'years_experience': 'Years of professional experience',
            'senior_roles': 'Senior roles held',
            'sector_expertise': 'Sector expertise',
            'privacy_level': 'Profile visibility',
            'project_work_available': 'Available for project work',
        }


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'journal', 'year', 'url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Publication title'}),
            'journal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Journal or conference name'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2030'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Link to publication'}),
        }


class PatentForm(forms.ModelForm):
    class Meta:
        model = Patent
        fields = ['title', 'patent_number', 'year', 'url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patent title'}),
            'patent_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patent number'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2030'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Link to patent'}),
        }


class NotableProjectForm(forms.ModelForm):
    class Meta:
        model = NotableProject
        fields = ['title', 'description', 'year', 'url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2030'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Link to project'}),
        }


class VerificationDocumentForm(forms.ModelForm):
    class Meta:
        model = VerificationDocument
        fields = ['document_type', 'file', 'description']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.png,.jpg,.jpeg'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief description of this document'}),
        }
