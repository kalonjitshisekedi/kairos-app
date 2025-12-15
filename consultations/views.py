"""
Views for consultations, bookings, and reviews.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
import uuid

from accounts.models import AuditLog
from experts.models import ExpertProfile
from availability.models import TimeSlot
from messaging.models import MessageThread
from .models import Booking, BookingNote, BookingAttachment, Review, ExpertClientRating, ConciergeRequest


@login_required
def create_booking(request, expert_id):
    expert = get_object_or_404(ExpertProfile, pk=expert_id, verification_status='verified')
    
    if request.method == 'POST':
        duration = int(request.POST.get('duration', 60))
        slot_id = request.POST.get('slot_id')
        problem_statement = request.POST.get('problem_statement', '')
        terms_accepted = request.POST.get('terms_accepted') == 'on'
        
        if not terms_accepted:
            messages.error(request, 'You must accept the terms to proceed.')
            return redirect('consultations:create_booking', expert_id=expert_id)
        
        slot = get_object_or_404(TimeSlot, pk=slot_id, expert=expert, status='available')
        
        if duration == 30:
            amount = expert.rate_30_min
        elif duration == 60:
            amount = expert.rate_60_min
        else:
            amount = expert.rate_90_min
        
        booking = Booking.objects.create(
            client=request.user,
            expert=expert,
            duration=duration,
            scheduled_start=slot.start_datetime,
            scheduled_end=slot.start_datetime + timedelta(minutes=duration),
            problem_statement=problem_statement,
            amount=amount,
            terms_accepted=True,
            terms_accepted_at=timezone.now(),
            status='requested',
            jitsi_room_id=f'kairos-{uuid.uuid4()}'
        )
        
        slots_needed = duration // 30
        current_slot = slot
        for i in range(slots_needed):
            if current_slot:
                current_slot.status = 'booked'
                current_slot.booking = booking
                current_slot.save()
                next_start = current_slot.start_datetime + timedelta(minutes=30)
                current_slot = TimeSlot.objects.filter(
                    expert=expert,
                    start_datetime=next_start,
                    status='available'
                ).first()
        
        MessageThread.objects.create(booking=booking)
        
        AuditLog.objects.create(
            user=request.user,
            event_type=AuditLog.EventType.BOOKING_CREATED,
            description=f'Booking created with {expert.user.full_name}',
            metadata={'booking_id': str(booking.id), 'amount': str(amount)}
        )
        
        send_mail(
            subject='New consultation request - Kairos',
            message=f'You have a new consultation request from {request.user.full_name}.\n\nProblem: {problem_statement}\n\nPlease log in to accept or decline.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[expert.user.email],
            fail_silently=True
        )
        
        if settings.PAYMENTS_ENABLED and amount > 0:
            return redirect('payments:checkout', booking_id=booking.id)
        else:
            booking.status = 'scheduled'
            booking.save()
            messages.success(request, 'Your consultation has been booked!')
            return redirect('consultations:booking_detail', pk=booking.id)
    
    from availability.models import TimeSlot
    available_slots = TimeSlot.objects.filter(
        expert=expert,
        status='available',
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')[:50]
    
    context = {
        'expert': expert,
        'available_slots': available_slots,
    }
    return render(request, 'consultations/create_booking.html', context)


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking.objects.select_related('expert__user', 'client'), pk=pk)
    
    if not (request.user == booking.client or request.user == booking.expert.user or request.user.is_admin):
        return HttpResponseForbidden()
    
    shared_notes = booking.notes.filter(note_type='shared')
    
    if request.user == booking.expert.user:
        expert_notes = booking.notes.filter(note_type='expert_private')
    else:
        expert_notes = None
    
    attachments = booking.attachments.all()
    
    try:
        thread = booking.message_thread
    except MessageThread.DoesNotExist:
        thread = MessageThread.objects.create(booking=booking)
    
    context = {
        'booking': booking,
        'shared_notes': shared_notes,
        'expert_notes': expert_notes,
        'attachments': attachments,
        'thread': thread,
        'messages': thread.messages.all()[:50],
    }
    return render(request, 'consultations/booking_detail.html', context)


@login_required
def session_room(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if not (request.user == booking.client or request.user == booking.expert.user):
        return HttpResponseForbidden()
    
    if booking.status not in ['scheduled', 'accepted', 'in_session']:
        messages.error(request, 'This session is not available.')
        return redirect('consultations:booking_detail', pk=pk)
    
    if booking.status != 'in_session':
        booking.status = 'in_session'
        booking.save()
        AuditLog.objects.create(
            user=request.user,
            event_type=AuditLog.EventType.BOOKING_STATUS_CHANGED,
            description=f'Session started',
            metadata={'booking_id': str(booking.id)}
        )
    
    shared_notes = booking.notes.filter(note_type='shared')
    expert_notes = booking.notes.filter(note_type='expert_private') if request.user == booking.expert.user else None
    
    context = {
        'booking': booking,
        'shared_notes': shared_notes,
        'expert_notes': expert_notes,
        'attachments': booking.attachments.all(),
    }
    return render(request, 'consultations/session_room.html', context)


@login_required
def add_note(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if not (request.user == booking.client or request.user == booking.expert.user):
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        note_type = request.POST.get('note_type', 'shared')
        
        if note_type == 'expert_private' and request.user != booking.expert.user:
            note_type = 'shared'
        
        BookingNote.objects.create(
            booking=booking,
            author=request.user,
            note_type=note_type,
            content=content
        )
        messages.success(request, 'Note added.')
    
    return redirect(request.META.get('HTTP_REFERER', 'consultations:booking_detail'), pk=pk)


@login_required
def upload_attachment(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if not (request.user == booking.client or request.user == booking.expert.user):
        return HttpResponseForbidden()
    
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        is_deliverable = request.POST.get('is_deliverable') == 'on' and request.user == booking.expert.user
        
        attachment = BookingAttachment.objects.create(
            booking=booking,
            uploaded_by=request.user,
            file=file,
            filename=file.name,
            file_size=file.size,
            description=request.POST.get('description', ''),
            is_deliverable=is_deliverable
        )
        
        AuditLog.objects.create(
            user=request.user,
            event_type=AuditLog.EventType.FILE_UPLOADED,
            description=f'File uploaded: {file.name}',
            metadata={'booking_id': str(booking.id), 'attachment_id': str(attachment.id)}
        )
        messages.success(request, 'File uploaded.')
    
    return redirect(request.META.get('HTTP_REFERER', 'consultations:booking_detail'), pk=pk)


@login_required
def mark_complete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if not (request.user == booking.client or request.user == booking.expert.user):
        return HttpResponseForbidden()
    
    if request.user == booking.expert.user:
        booking.completed_by_expert = True
    else:
        booking.completed_by_client = True
    
    if booking.completed_by_expert and booking.completed_by_client:
        booking.status = 'completed'
        booking.completed_at = timezone.now()
        
        expert = booking.expert
        expert.total_consultations += 1
        expert.total_earnings += booking.amount
        expert.save()
        
        AuditLog.objects.create(
            user=request.user,
            event_type=AuditLog.EventType.BOOKING_STATUS_CHANGED,
            description='Session completed',
            metadata={'booking_id': str(booking.id)}
        )
        
        send_mail(
            subject='Consultation completed - Kairos',
            message=f'Your consultation has been marked as complete. Please log in to leave a review.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.client.email],
            fail_silently=True
        )
    
    booking.save()
    messages.success(request, 'Session marked as complete.')
    return redirect('consultations:booking_detail', pk=pk)


@login_required
def leave_review(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.user != booking.client:
        return HttpResponseForbidden()
    
    if booking.status != 'completed':
        messages.error(request, 'You can only review completed sessions.')
        return redirect('consultations:booking_detail', pk=pk)
    
    if hasattr(booking, 'review'):
        messages.error(request, 'You have already reviewed this session.')
        return redirect('consultations:booking_detail', pk=pk)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        
        Review.objects.create(
            booking=booking,
            reviewer=request.user,
            reviewee=booking.expert.user,
            rating=rating,
            comment=comment,
            is_public=True
        )
        
        expert = booking.expert
        reviews = Review.objects.filter(reviewee=booking.expert.user, is_public=True)
        expert.average_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0
        expert.total_reviews = reviews.count()
        expert.save()
        
        messages.success(request, 'Thank you for your review!')
        return redirect('consultations:booking_detail', pk=pk)
    
    return render(request, 'consultations/leave_review.html', {'booking': booking})


@login_required
def expert_rate_client(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.user != booking.expert.user:
        return HttpResponseForbidden()
    
    if hasattr(booking, 'expert_client_rating'):
        messages.error(request, 'You have already rated this client.')
        return redirect('consultations:booking_detail', pk=pk)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        notes = request.POST.get('notes', '')
        
        ExpertClientRating.objects.create(
            booking=booking,
            expert=booking.expert,
            client=booking.client,
            rating=rating,
            notes=notes
        )
        
        messages.success(request, 'Client rating saved.')
        return redirect('consultations:booking_detail', pk=pk)
    
    return render(request, 'consultations/rate_client.html', {'booking': booking})


@login_required
def accept_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.user != booking.expert.user:
        return HttpResponseForbidden()
    
    if booking.status != 'requested':
        messages.error(request, 'This booking cannot be accepted.')
        return redirect('consultations:booking_detail', pk=pk)
    
    booking.status = 'accepted'
    booking.responded_at = timezone.now()
    booking.save()
    
    AuditLog.objects.create(
        user=request.user,
        event_type=AuditLog.EventType.BOOKING_STATUS_CHANGED,
        description='Booking accepted',
        metadata={'booking_id': str(booking.id)}
    )
    
    send_mail(
        subject='Consultation accepted - Kairos',
        message=f'Your consultation with {booking.expert.user.full_name} has been accepted.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.client.email],
        fail_silently=True
    )
    
    messages.success(request, 'Booking accepted.')
    return redirect('consultations:booking_detail', pk=pk)


@login_required
def decline_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.user != booking.expert.user:
        return HttpResponseForbidden()
    
    if booking.status != 'requested':
        messages.error(request, 'This booking cannot be declined.')
        return redirect('consultations:booking_detail', pk=pk)
    
    booking.status = 'cancelled'
    booking.responded_at = timezone.now()
    booking.cancelled_at = timezone.now()
    booking.cancelled_by = request.user
    booking.cancellation_reason = request.POST.get('reason', 'Declined by expert')
    booking.save()
    
    TimeSlot.objects.filter(booking=booking).update(status='available', booking=None)
    
    messages.success(request, 'Booking declined.')
    return redirect('experts:dashboard')


@login_required
def create_concierge_request(request):
    if request.method == 'POST':
        description = request.POST.get('description', '')
        budget_min = request.POST.get('budget_min') or None
        budget_max = request.POST.get('budget_max') or None
        timeline = request.POST.get('timeline', '')
        
        concierge = ConciergeRequest.objects.create(
            client=request.user,
            description=description,
            budget_min=budget_min,
            budget_max=budget_max,
            timeline=timeline
        )
        
        send_mail(
            subject='New concierge request - Kairos',
            message=f'New concierge request from {request.user.full_name}:\n\n{description}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True
        )
        
        messages.success(request, 'Your request has been submitted. Our team will match you with the right expert.')
        return redirect('accounts:dashboard')
    
    from experts.models import ExpertiseTag
    tags = ExpertiseTag.objects.all()
    return render(request, 'consultations/concierge_request.html', {'tags': tags})


@login_required
def my_bookings(request):
    if request.user.is_expert:
        try:
            profile = request.user.expert_profile
            bookings = Booking.objects.filter(expert=profile).order_by('-created_at')
        except:
            bookings = Booking.objects.none()
    else:
        bookings = Booking.objects.filter(client=request.user).order_by('-created_at')
    
    return render(request, 'consultations/my_bookings.html', {'bookings': bookings})
