"""
Expert profile models with verification workflow.
"""
import uuid
from django.conf import settings
from django.db import models


class ExpertiseTag(models.Model):
    class TagType(models.TextChoices):
        DISCIPLINE = 'discipline', 'Discipline'
        INDUSTRY = 'industry', 'Industry'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    tag_type = models.CharField(max_length=20, choices=TagType.choices, default=TagType.DISCIPLINE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'experts_expertise_tag'
        ordering = ['name']

    def __str__(self):
        return self.name


class ExpertProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        APPLIED = 'applied', 'Applied'
        VETTED = 'vetted', 'Vetted'
        ACTIVE = 'active', 'Active'
        NEEDS_CHANGES = 'needs_changes', 'Needs changes'
        REJECTED = 'rejected', 'Rejected'

    class PrivacyLevel(models.TextChoices):
        PUBLIC = 'public', 'Public'
        SEMI_PRIVATE = 'semi_private', 'Semi-private'
        PRIVATE = 'private', 'Private'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expert_profile')
    headline = models.CharField(max_length=200, blank=True, help_text='One sentence describing your expertise')
    bio = models.TextField(blank=True, help_text='Detailed biography')
    pronouns = models.CharField(max_length=50, blank=True)
    affiliation = models.CharField(max_length=200, blank=True, help_text='Current organisation or institution')
    location = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    languages = models.JSONField(default=list, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    expertise_tags = models.ManyToManyField(ExpertiseTag, blank=True, related_name='experts')
    orcid_id = models.CharField(max_length=50, blank=True, help_text='ORCID identifier')
    linkedin_url = models.URLField(blank=True, help_text='LinkedIn profile URL')
    github_url = models.URLField(blank=True, help_text='GitHub profile URL')
    cv_file = models.FileField(upload_to='cvs/', blank=True, null=True, help_text='CV file (PDF or DOCX)')
    years_experience = models.IntegerField(default=0, help_text='Years of professional experience')
    senior_roles = models.TextField(blank=True, help_text='Senior positions held')
    sector_expertise = models.TextField(blank=True, help_text='Industry sectors of expertise')
    privacy_level = models.CharField(
        max_length=20,
        choices=PrivacyLevel.choices,
        default=PrivacyLevel.SEMI_PRIVATE,
        help_text='Controls profile visibility'
    )
    is_featured = models.BooleanField(default=False, help_text='Featured on homepage')
    internal_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Internal pricing - admin only')
    expert_payout_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Expert payout rate - expert only')
    project_work_available = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.APPLIED
    )
    verification_submitted_at = models.DateTimeField(blank=True, null=True)
    verification_reviewed_at = models.DateTimeField(blank=True, null=True)
    verification_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_experts'
    )
    verification_notes = models.TextField(blank=True, help_text='Internal notes from admin review')
    is_publicly_listed = models.BooleanField(default=False)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    total_consultations = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'experts_profile'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.full_name} - Expert'

    @property
    def is_verified(self):
        return self.verification_status in [self.VerificationStatus.VETTED, self.VerificationStatus.ACTIVE]

    @property
    def is_active(self):
        return self.verification_status == self.VerificationStatus.ACTIVE

    @property
    def profile_completeness(self):
        fields = [
            bool(self.headline),
            bool(self.bio),
            bool(self.avatar),
            bool(self.affiliation),
            bool(self.location),
            self.expertise_tags.exists(),
            self.years_experience > 0,
            self.publications.exists(),
            self.verification_documents.exists(),
            bool(self.languages),
        ]
        return int((sum(fields) / len(fields)) * 100)

    @property
    def missing_sections(self):
        missing = []
        if not self.headline:
            missing.append('Add a headline describing your expertise')
        if not self.bio:
            missing.append('Write a detailed biography')
        if not self.avatar:
            missing.append('Upload a professional photo')
        if not self.affiliation:
            missing.append('Add your current affiliation')
        if not self.location:
            missing.append('Specify your location')
        if not self.expertise_tags.exists():
            missing.append('Select your areas of expertise')
        if self.years_experience == 0:
            missing.append('Specify your years of experience')
        if not self.publications.exists():
            missing.append('Add at least one publication or project')
        if not self.verification_documents.exists():
            missing.append('Upload verification documents')
        if not self.languages:
            missing.append('Specify languages you speak')
        return missing

    def calculate_average_response_time(self):
        from consultations.models import Booking
        recent_bookings = Booking.objects.filter(
            expert=self,
            responded_at__isnull=False
        ).order_by('-created_at')[:10]
        if not recent_bookings:
            return None
        total_hours = sum(
            (b.responded_at - b.created_at).total_seconds() / 3600
            for b in recent_bookings
        )
        return round(total_hours / len(recent_bookings), 1)


class Publication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expert = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=500)
    url = models.URLField(blank=True)
    year = models.IntegerField(blank=True, null=True)
    journal = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'experts_publication'
        ordering = ['-year', 'title']

    def __str__(self):
        return self.title


class Patent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expert = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE, related_name='patents')
    title = models.CharField(max_length=500)
    patent_number = models.CharField(max_length=100, blank=True)
    url = models.URLField(blank=True)
    year = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'experts_patent'
        ordering = ['-year', 'title']

    def __str__(self):
        return self.title


class NotableProject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expert = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE, related_name='notable_projects')
    title = models.CharField(max_length=300)
    description = models.TextField()
    url = models.URLField(blank=True)
    year = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'experts_notable_project'
        ordering = ['-year', 'title']

    def __str__(self):
        return self.title


class VerificationDocument(models.Model):
    class DocumentType(models.TextChoices):
        DEGREE_CERTIFICATE = 'degree', 'Degree certificate'
        EMPLOYMENT_LETTER = 'employment', 'Employment letter'
        OTHER = 'other', 'Other documentation'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expert = models.ForeignKey(ExpertProfile, on_delete=models.CASCADE, related_name='verification_documents')
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    file = models.FileField(upload_to='verification_documents/')
    description = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'experts_verification_document'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.get_document_type_display()} - {self.expert}'


class ExpertApplication(models.Model):
    class ApplicationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    orcid_id = models.CharField(max_length=50, blank=True)
    expertise_areas = models.TextField()
    years_experience = models.IntegerField(default=0)
    bio = models.TextField(blank=True)
    cv_file = models.FileField(upload_to='applications/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.PENDING)
    popia_consent = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'experts_application'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} - {self.get_status_display()}'
