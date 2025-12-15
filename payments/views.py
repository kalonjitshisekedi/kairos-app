"""
Views for Stripe payment integration.
"""
import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.models import AuditLog
from consultations.models import Booking
from .models import Payment, Invoice

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request, booking_id):
    if not settings.PAYMENTS_ENABLED:
        messages.info(request, 'Payments are currently disabled.')
        booking = get_object_or_404(Booking, pk=booking_id, client=request.user)
        booking.status = 'scheduled'
        booking.save()
        return redirect('consultations:booking_detail', pk=booking_id)
    
    booking = get_object_or_404(Booking, pk=booking_id, client=request.user)
    
    if hasattr(booking, 'payment') and booking.payment.status == 'completed':
        messages.info(request, 'This booking has already been paid.')
        return redirect('consultations:booking_detail', pk=booking_id)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': f'Consultation with {booking.expert.user.full_name}',
                        'description': f'{booking.duration} minute consultation',
                    },
                    'unit_amount': int(booking.amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=settings.SITE_URL + f'/payments/success/{booking.id}/',
            cancel_url=settings.SITE_URL + f'/payments/cancel/{booking.id}/',
            metadata={
                'booking_id': str(booking.id),
            },
        )
        
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'payer': request.user,
                'amount': booking.amount,
                'stripe_checkout_session_id': checkout_session.id,
            }
        )
        if not created:
            payment.stripe_checkout_session_id = checkout_session.id
            payment.save()
        
        return redirect(checkout_session.url)
    
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('consultations:booking_detail', pk=booking_id)


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, client=request.user)
    
    try:
        payment = booking.payment
        if payment.status != 'completed':
            session = stripe.checkout.Session.retrieve(payment.stripe_checkout_session_id)
            if session.payment_status == 'paid':
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.stripe_payment_intent_id = session.payment_intent
                payment.save()
                
                booking.status = 'scheduled'
                booking.save()
                
                AuditLog.objects.create(
                    user=request.user,
                    event_type=AuditLog.EventType.PAYMENT_RECEIVED,
                    description=f'Payment of {payment.amount} {payment.currency} received',
                    metadata={'booking_id': str(booking.id), 'payment_id': str(payment.id)}
                )
                
                Invoice.objects.create(
                    booking=booking,
                    payment=payment,
                    expert=booking.expert,
                    client=request.user,
                    amount=payment.amount,
                    currency=payment.currency,
                    status='paid',
                    issued_at=timezone.now(),
                    paid_at=timezone.now()
                )
    except Exception:
        pass
    
    messages.success(request, 'Payment successful! Your consultation is now booked.')
    return redirect('consultations:booking_detail', pk=booking_id)


@login_required
def payment_cancel(request, booking_id):
    messages.warning(request, 'Payment was cancelled. You can try again when ready.')
    return redirect('consultations:booking_detail', pk=booking_id)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = session['metadata'].get('booking_id')
        
        if booking_id:
            try:
                booking = Booking.objects.get(pk=booking_id)
                payment = booking.payment
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.stripe_payment_intent_id = session.get('payment_intent')
                payment.save()
                
                booking.status = 'scheduled'
                booking.save()
            except (Booking.DoesNotExist, Payment.DoesNotExist):
                pass
    
    return HttpResponse(status=200)


@login_required
def my_payments(request):
    payments = Payment.objects.filter(payer=request.user).select_related('booking__expert__user').order_by('-created_at')
    return render(request, 'payments/my_payments.html', {'payments': payments})


@login_required
def my_invoices(request):
    if request.user.is_expert:
        try:
            profile = request.user.expert_profile
            invoices = Invoice.objects.filter(expert=profile).order_by('-created_at')
        except:
            invoices = Invoice.objects.none()
    else:
        invoices = Invoice.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'payments/my_invoices.html', {'invoices': invoices})
