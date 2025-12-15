"""
Context processors for site-wide settings.
"""
from django.conf import settings


def site_settings(request):
    return {
        'SITE_NAME': 'Kairos',
        'TAGLINE': "don't guess. know",
        'PAYMENTS_ENABLED': settings.PAYMENTS_ENABLED,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    }
