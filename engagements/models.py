"""
Engagement workflow models for Kairos platform.
"""
import uuid
from django.conf import settings
from django.db import models

from .enums import (
    ClientRequestStatus,
    EngagementType,
    UrgencyLevel,
    ConfidentialityLevel,
    ExpertMatchStatus,
    EngagementStatus,
    MeetingMode,
    ProgressEventType,
)


class ClientRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='engagement_requests'
    )
    organisation_name = models.CharField(max_length=200)
    billing_email = models.EmailField(blank=True, help_text='Required for invoicing')
    phone = models.CharField(max_length=30, default='+27', help_text='Contact phone number')
    engagement_type = models.CharField(
        max_length=20,
        choices=EngagementType.choices,
        default=EngagementType.CONSULTATION
    )
    urgency = models.CharField(
        max_length=20,
        choices=UrgencyLevel.choices,
        default=UrgencyLevel.STANDARD
    )
    brief = models.TextField(help_text='Describe the challenge or problem you need help with')
    attachment = models.FileField(
        upload_to='engagement_briefs/',
        blank=True,
        null=True,
        help_text='Upload a brief document (PDF/DOCX)'
    )
    confidentiality_level = models.CharField(
        max_length=20,
        choices=ConfidentialityLevel.choices,
        default=ConfidentialityLevel.STANDARD
    )
    status = models.CharField(
        max_length=20,
        choices=ClientRequestStatus.choices,
        default=ClientRequestStatus.SUBMITTED
    )
    admin_notes = models.TextField(blank=True, help_text='Internal notes for admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'engagements_client_request'
        ordering = ['-created_at']

    def __str__(self):
        return f'Request from {self.organisation_name} - {self.get_status_display()}'

    def can_view_experts(self, user):
        if user.is_admin:
            return True
        if user.client_status != 'verified':
            return False
        if user != self.client:
            return False
        return self.status not in [
            ClientRequestStatus.SUBMITTED,
            ClientRequestStatus.IN_REVIEW,
            ClientRequestStatus.CANCELLED,
            ClientRequestStatus.EXPIRED,
        ]

    def advance(self, event_type, actor=None):
        ProgressEvent.objects.create(
            request=self,
            actor=actor,
            event_type=event_type,
            message=f'Status changed to {self.get_status_display()}'
        )
        self.save()


class ExpertMatch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(
        ClientRequest,
        on_delete=models.CASCADE,
        related_name='expert_matches'
    )
    expert = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='match_proposals'
    )
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='proposed_matches'
    )
    status = models.CharField(
        max_length=20,
        choices=ExpertMatchStatus.choices,
        default=ExpertMatchStatus.PROPOSED
    )
    note_to_client = models.TextField(blank=True, help_text='Note visible to client')
    internal_note = models.TextField(blank=True, help_text='Internal admin note')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'engagements_expert_match'
        ordering = ['-created_at']
        verbose_name = 'Expert match'
        verbose_name_plural = 'Expert matches'

    def __str__(self):
        return f'{self.expert.full_name} for {self.request.organisation_name} - {self.get_status_display()}'


class Engagement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(
        ClientRequest,
        on_delete=models.CASCADE,
        related_name='engagements'
    )
    expert = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expert_engagements'
    )
    status = models.CharField(
        max_length=20,
        choices=EngagementStatus.choices,
        default=EngagementStatus.SCHEDULED
    )
    scheduled_start = models.DateTimeField(blank=True, null=True)
    scheduled_end = models.DateTimeField(blank=True, null=True)
    meeting_mode = models.CharField(
        max_length=20,
        choices=MeetingMode.choices,
        default=MeetingMode.PLATFORM
    )
    meeting_link = models.URLField(blank=True, help_text='External meeting link if applicable')
    shared_notes = models.TextField(blank=True, help_text='Notes visible to both parties')
    private_expert_notes = models.TextField(blank=True, help_text='Private notes for expert only')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'engagements_engagement'
        ordering = ['-created_at']

    def __str__(self):
        return f'Engagement: {self.request.organisation_name} with {self.expert.full_name}'

    def advance(self, new_status, actor=None):
        old_status = self.status
        self.status = new_status
        self.save()
        ProgressEvent.objects.create(
            request=self.request,
            actor=actor,
            event_type=ProgressEventType.STATUS_CHANGED,
            message=f'Engagement status changed from {old_status} to {new_status}'
        )


class ProgressEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(
        ClientRequest,
        on_delete=models.CASCADE,
        related_name='progress_events'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_events'
    )
    event_type = models.CharField(
        max_length=30,
        choices=ProgressEventType.choices
    )
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'engagements_progress_event'
        ordering = ['created_at']
        verbose_name = 'Progress event'
        verbose_name_plural = 'Progress events'

    def __str__(self):
        return f'{self.get_event_type_display()} - {self.created_at}'
