"""
Centralised status enums for Kairos workflow models.
"""
from django.db import models


class ClientStatus(models.TextChoices):
    PENDING = 'pending', 'Pending verification'
    VERIFIED = 'verified', 'Verified'
    REJECTED = 'rejected', 'Rejected'


class ExpertStatus(models.TextChoices):
    APPLIED = 'applied', 'Applied'
    VETTED = 'vetted', 'Vetted'
    ACTIVE = 'active', 'Active'
    REJECTED = 'rejected', 'Rejected'


class ClientRequestStatus(models.TextChoices):
    SUBMITTED = 'submitted', 'Submitted'
    IN_REVIEW = 'in_review', 'In review'
    SHORTLISTED = 'shortlisted', 'Experts shortlisted'
    PROPOSAL_SENT = 'proposal_sent', 'Proposal sent'
    CONFIRMED = 'confirmed', 'Confirmed'
    IN_PROGRESS = 'in_progress', 'In progress'
    AWAITING_CLIENT = 'awaiting_client', 'Awaiting client confirmation'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    EXPIRED = 'expired', 'Expired'


class EngagementType(models.TextChoices):
    CONSULTATION = 'consultation', 'Consultation'
    RESEARCH = 'research', 'Research'
    ADVISORY = 'advisory', 'Advisory'


class UrgencyLevel(models.TextChoices):
    STANDARD = 'standard', 'Standard (2-4 weeks)'
    URGENT = 'urgent', 'Urgent (within 1 week)'


class ConfidentialityLevel(models.TextChoices):
    STANDARD = 'standard', 'Standard'
    RESTRICTED = 'restricted', 'Restricted'


class ExpertMatchStatus(models.TextChoices):
    PROPOSED = 'proposed', 'Proposed'
    DECLINED = 'declined', 'Declined'
    ACCEPTED = 'accepted', 'Accepted'
    EXPIRED = 'expired', 'Expired'


class EngagementStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    IN_PROGRESS = 'in_progress', 'In progress'
    AWAITING_CLIENT_CONFIRMATION = 'awaiting_client', 'Awaiting client confirmation'
    COMPLETED = 'completed', 'Completed'
    ARCHIVED = 'archived', 'Archived'
    CANCELLED = 'cancelled', 'Cancelled'


class MeetingMode(models.TextChoices):
    PLATFORM = 'platform', 'Platform'
    ADMIN_FACILITATED = 'admin_facilitated', 'Admin facilitated'


class ProgressEventType(models.TextChoices):
    REQUEST_SUBMITTED = 'request_submitted', 'Request submitted'
    REQUEST_IN_REVIEW = 'request_in_review', 'Request in review'
    EXPERT_SHORTLISTED = 'expert_shortlisted', 'Expert shortlisted'
    EXPERT_PROPOSED = 'expert_proposed', 'Expert proposed'
    EXPERT_ACCEPTED = 'expert_accepted', 'Expert accepted'
    EXPERT_DECLINED = 'expert_declined', 'Expert declined'
    PROPOSAL_SENT = 'proposal_sent', 'Proposal sent'
    CLIENT_CONFIRMED = 'client_confirmed', 'Client confirmed'
    ENGAGEMENT_SCHEDULED = 'engagement_scheduled', 'Engagement scheduled'
    ENGAGEMENT_STARTED = 'engagement_started', 'Engagement started'
    ENGAGEMENT_COMPLETED = 'engagement_completed', 'Engagement completed'
    REQUEST_CANCELLED = 'request_cancelled', 'Request cancelled'
    REQUEST_EXPIRED = 'request_expired', 'Request expired'
    NOTE_ADDED = 'note_added', 'Note added'
    STATUS_CHANGED = 'status_changed', 'Status changed'
