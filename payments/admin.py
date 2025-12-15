"""
Admin configuration for payments app.
"""
from django.contrib import admin
from .models import Payment, Invoice, ExpertPayout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'payer', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency']
    search_fields = ['payer__email', 'stripe_payment_intent_id']
    readonly_fields = ['stripe_checkout_session_id', 'stripe_payment_intent_id', 'created_at', 'paid_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'booking', 'client', 'expert', 'amount', 'status']
    list_filter = ['status']
    search_fields = ['invoice_number', 'client__email']


@admin.register(ExpertPayout)
class ExpertPayoutAdmin(admin.ModelAdmin):
    list_display = ['expert', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['expert__user__email']
