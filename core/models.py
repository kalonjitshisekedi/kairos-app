"""
Core models for the Kairos platform.
"""
from django.db import models


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
