"""
Consultation, booking, and review models.
"""
import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class ClientRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending review'
        IN_REVIEW = 'in_review', 'In review'
        MATCHED = 'matched', 'Expert matched'
        PROPOSAL_SENT = 'proposal_sent', 'Proposal sent'
        CONFIRMED = 'confirmed', 'Confirmed'
        IN_PROGRESS = 'in_progress', 'In progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        EXPIRED = 'expired', 'Expired'

    class EngagementType(models.TextChoices):
        CONSULTATION = 'consultation', 'Consultation'
        RESEARCH = 'research', 'Research'
        ADVISORY = 'advisory', 'Advisory'

    class UrgencyLevel(models.TextChoices):
        LOW = 'low', 'Standard (2-4 weeks)'
        MEDIUM = 'medium', 'Priority (1-2 weeks)'
        HIGH = 'high', 'Urgent (within 1 week)'
        CRITICAL = 'critical', 'Critical (within 48 hours)'

    class ConfidentialityLevel(models.TextChoices):
        STANDARD = 'standard', 'Standard'
        ELEVATED = 'elevated', 'Elevated'
        STRICT = 'strict', 'Strict NDA required'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    email = models.EmailField()
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_requests')
    problem_description = models.TextField(help_text='Describe the challenge or problem you need help with')
    engagement_type = models.CharField(max_length=20, choices=EngagementType.choices, default=EngagementType.CONSULTATION)
    timeline_urgency = models.CharField(max_length=20, choices=UrgencyLevel.choices, default=UrgencyLevel.LOW)
    confidentiality_level = models.CharField(max_length=20, choices=ConfidentialityLevel.choices, default=ConfidentialityLevel.STANDARD)
    preferred_expertise = models.ManyToManyField('experts.ExpertiseTag', blank=True, related_name='client_requests')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    matched_expert = models.ForeignKey('experts.ExpertProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='matched_client_requests')
    matched_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='matched_client_requests')
    matched_at = models.DateTimeField(blank=True, null=True)
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Admin-set engagement price')
    expert_payout = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Expert payout amount')
    admin_notes = models.TextField(blank=True)
    internal_priority = models.IntegerField(default=0, help_text='Internal priority score')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultations_client_request'
        ordering = ['-created_at']

    def __str__(self):
        return f'Request from {self.company} ({self.name}) - {self.get_status_display()}'


class ConciergeRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        MATCHED = 'matched', 'Matched'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        EXPIRED = 'expired', 'Expired'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='concierge_requests')
    description = models.TextField(help_text='Describe what you need help with')
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    timeline = models.CharField(max_length=200, blank=True)
    preferred_expertise = models.ManyToManyField('experts.ExpertiseTag', blank=True, related_name='concierge_requests')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    matched_expert = models.ForeignKey('experts.ExpertProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='matched_requests')
    matched_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='matched_concierge_requests')
    matched_at = models.DateTimeField(blank=True, null=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultations_concierge_request'
        ordering = ['-created_at']

    def __str__(self):
        return f'Request from {self.client.email} - {self.status}'


class Booking(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        REQUESTED = 'requested', 'Requested'
        ACCEPTED = 'accepted', 'Accepted'
        SCHEDULED = 'scheduled', 'Scheduled'
        IN_SESSION = 'in_session', 'In session'
        COMPLETED = 'completed', 'Completed'
        ARCHIVED = 'archived', 'Archived'
        CANCELLED = 'cancelled', 'Cancelled'
        DISPUTED = 'disputed', 'Disputed'

    class ServiceType(models.TextChoices):
        CONSULTATION = 'consultation', 'Consultation'
        RESEARCH = 'research', 'Research'
        ADVISORY = 'advisory', 'Advisory'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings_as_client')
    expert = models.ForeignKey('experts.ExpertProfile', on_delete=models.CASCADE, related_name='bookings')
    client_request = models.ForeignKey(ClientRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    concierge_request = models.ForeignKey(ConciergeRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    service_type = models.CharField(max_length=20, choices=ServiceType.choices, default=ServiceType.CONSULTATION)
    scope = models.TextField(blank=True, help_text='Scope of the engagement')
    duration_description = models.CharField(max_length=200, blank=True, help_text='Duration description e.g. 2 weeks')
    scheduled_start = models.DateTimeField(blank=True, null=True)
    scheduled_end = models.DateTimeField(blank=True, null=True)
    problem_statement = models.TextField(help_text='Brief description of what you need help with')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    jitsi_room_id = models.CharField(max_length=100, blank=True)
    external_meeting_link = models.URLField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Engagement price - set by admin')
    expert_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Expert payout amount')
    currency = models.CharField(max_length=3, default='GBP')
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    completed_by_expert = models.BooleanField(default=False)
    completed_by_client = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancelled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_bookings')

    class Meta:
        db_table = 'consultations_booking'
        ordering = ['-created_at']

    def __str__(self):
        return f'Booking {self.id} - {self.client.email} with {self.expert}'

    def save(self, *args, **kwargs):
        if not self.jitsi_room_id:
            self.jitsi_room_id = f'kairos-{self.id}'
        super().save(*args, **kwargs)

    @property
    def meeting_url(self):
        if self.external_meeting_link:
            return self.external_meeting_link
        return f'https://meet.jit.si/{self.jitsi_room_id}'

    def calculate_amount(self):
        if self.duration == self.Duration.THIRTY:
            return self.expert.rate_30_min
        elif self.duration == self.Duration.SIXTY:
            return self.expert.rate_60_min
        elif self.duration == self.Duration.NINETY:
            return self.expert.rate_90_min
        return 0


class BookingNote(models.Model):
    class NoteType(models.TextChoices):
        SHARED = 'shared', 'Shared note'
        EXPERT_PRIVATE = 'expert_private', 'Expert private note'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='booking_notes')
    note_type = models.CharField(max_length=20, choices=NoteType.choices, default=NoteType.SHARED)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultations_booking_note'
        ordering = ['created_at']

    def __str__(self):
        return f'Note on {self.booking} by {self.author}'


class BookingAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='booking_attachments')
    file = models.FileField(upload_to='booking_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0)
    description = models.CharField(max_length=300, blank=True)
    is_deliverable = models.BooleanField(default=False, help_text='Is this a deliverable from the expert?')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consultations_booking_attachment'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.filename} on {self.booking}'


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultations_review'
        ordering = ['-created_at']

    def __str__(self):
        return f'Review by {self.reviewer} for {self.reviewee} - {self.rating}/5'


class ExpertClientRating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='expert_client_rating')
    expert = models.ForeignKey('experts.ExpertProfile', on_delete=models.CASCADE, related_name='client_ratings')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings_from_experts')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    notes = models.TextField(blank=True, help_text='Private notes about this client')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consultations_expert_client_rating'

    def __str__(self):
        return f'Rating of {self.client} by {self.expert} - {self.rating}/5'
