"""
Payment models for Stripe integration.
"""
import uuid
from django.conf import settings
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
        PARTIALLY_REFUNDED = 'partially_refunded', 'Partially refunded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField('consultations.Booking', on_delete=models.CASCADE, related_name='payment')
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GBP')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_receipt_url = models.URLField(blank=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_payment'
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment {self.id} - {self.amount} {self.currency} - {self.status}'


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ISSUED = 'issued', 'Issued'
        PAID = 'paid', 'Paid'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    booking = models.ForeignKey('consultations.Booking', on_delete=models.CASCADE, related_name='invoices')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    expert = models.ForeignKey('experts.ExpertProfile', on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GBP')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    description = models.TextField(blank=True)
    issued_at = models.DateTimeField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_invoice'
        ordering = ['-created_at']

    def __str__(self):
        return f'Invoice {self.invoice_number}'

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            self.invoice_number = f'KAI-{timezone.now().strftime("%Y%m%d")}-{str(self.id)[:8].upper()}'
        super().save(*args, **kwargs)


class ExpertPayout(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expert = models.ForeignKey('experts.ExpertProfile', on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GBP')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    bookings = models.ManyToManyField('consultations.Booking', related_name='payouts')
    stripe_transfer_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_expert_payout'
        ordering = ['-created_at']

    def __str__(self):
        return f'Payout {self.id} to {self.expert} - {self.amount} {self.currency}'
