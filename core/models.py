"""
Core models for the Kairos platform.
"""
import uuid
from django.db import models


class ContactInquiry(models.Model):
    class InquiryType(models.TextChoices):
        GENERAL = 'general', 'General Inquiry'
        PROJECT = 'project', 'Project Matching'
        PARTNERSHIP = 'partnership', 'Business Partnership'
        SUPPORT = 'support', 'Technical Support'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    company = models.CharField(max_length=200, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=InquiryType.choices, default=InquiryType.GENERAL)
    message = models.TextField()
    popia_consent = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_contact_inquiry'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.get_inquiry_type_display()}'


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='Kairos')
    tagline = models.CharField(max_length=200, default="don't guess. know")
    contact_email = models.EmailField(default='support@kairos.example.com')
    support_email = models.EmailField(default='support@kairos.example.com')
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    terms_version = models.CharField(max_length=20, default='1.0')
    privacy_policy_version = models.CharField(max_length=20, default='1.0')
    acceptable_use_version = models.CharField(max_length=20, default='1.0')
    maintenance_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_site_settings'
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return f'{self.site_name} settings'

    @classmethod
    def get_settings(cls):
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings
