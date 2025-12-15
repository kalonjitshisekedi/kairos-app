"""
URL configuration for payments app.
"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<uuid:booking_id>/', views.checkout, name='checkout'),
    path('success/<uuid:booking_id>/', views.payment_success, name='success'),
    path('cancel/<uuid:booking_id>/', views.payment_cancel, name='cancel'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('my-payments/', views.my_payments, name='my_payments'),
    path('invoices/', views.my_invoices, name='my_invoices'),
]
