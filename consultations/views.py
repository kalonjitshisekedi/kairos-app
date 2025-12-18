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
from experts.models import ExpertProfile, ExpertiseTag
from availability.models import TimeSlot
from messaging.models import MessageThread
from .models import Booking, BookingNote, BookingAttachment, Review, ExpertClientRating, ConciergeRequest, ClientRequest


@login_required
def create_booking(request, expert_id):
    expert = get_object_or_404(ExpertProfile, pk=expert_id, verification_status__in=['vetted', 'active'])
    
    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        problem_statement = request.POST.get('problem_statement', '')
        service_type = request.POST.get('service_type', 'consultation')
        terms_accepted = request.POST.get('terms_accepted') == 'on'
        
        if not terms_accepted:
            messages.error(request, 'You must accept the terms to proceed.')
            return redirect('consultations:create_booking', expert_id=expert_id)
        
        slot = get_object_or_404(TimeSlot, pk=slot_id, expert=expert, status='available')
        
        booking = Booking.objects.create(
            client=request.user,
            expert=expert,
            service_type=service_type,
            scheduled_start=slot.start_datetime,
            scheduled_end=slot.start_datetime + timedelta(minutes=60),
            problem_statement=problem_statement,
            amount=0,
            terms_accepted=True,
            terms_accepted_at=timezone.now(),
            status='requested',
            jitsi_room_id=f'kairos-{uuid.uuid4()}'
        )
        
        slot.status = 'booked'
        slot.booking = booking
        slot.save()
        
        MessageThread.objects.create(booking=booking)
        
        AuditLog.objects.create(
            user=request.user,
            event_type=AuditLog.EventType.BOOKING_CREATED,
            description=f'Booking created with {expert.user.full_name}',
            metadata={'booking_id': str(booking.id), 'service_type': service_type}
        )
        
        send_mail(
            subject='New engagement request - Kairos',
            message=f'You have a new engagement request from {request.user.full_name}.\n\nProblem: {problem_statement}\n\nPlease log in to accept or decline.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[expert.user.email],
            fail_silently=True
        )
        
        messages.success(request, 'Your request has been submitted. The expert will be notified.')
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


def submit_client_request(request):
    """Submit a client request for expert matching - concierge flow.
    Supports pre-selecting an expert via ?expert_id=<uuid> query param.
    """
    preferred_expert = None
    expert_id = request.GET.get('expert_id')
    if expert_id:
        try:
            preferred_expert = ExpertProfile.objects.get(pk=expert_id)
        except ExpertProfile.DoesNotExist:
            pass
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        company = request.POST.get('company', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        problem_description = request.POST.get('problem_description', '')
        engagement_type = request.POST.get('engagement_type', 'consultation')
        timeline_urgency = request.POST.get('timeline_urgency', 'low')
        confidentiality_level = request.POST.get('confidentiality_level', 'standard')
        budget_range = request.POST.get('budget_range', '')
        consent = request.POST.get('consent') == 'on'
        
        brief_document = request.FILES.get('brief_document')
        if brief_document:
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_ext = '.' + brief_document.name.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                messages.error(request, 'Invalid file type. Please upload a PDF or DOCX file.')
                return redirect('consultations:submit_request')
            if brief_document.size > 10 * 1024 * 1024:
                messages.error(request, 'File too large. Maximum size is 10MB.')
                return redirect('consultations:submit_request')
        
        # Get preferred expert from form or query param
        preferred_expert_id = request.POST.get('preferred_expert') or expert_id
        preferred_expert_obj = None
        if preferred_expert_id:
            try:
                preferred_expert_obj = ExpertProfile.objects.get(pk=preferred_expert_id)
            except ExpertProfile.DoesNotExist:
                pass
        
        client_request = ClientRequest.objects.create(
            name=name,
            company=company,
            email=email,
            phone=phone,
            client=request.user if request.user.is_authenticated else None,
            problem_description=problem_description,
            engagement_type=engagement_type,
            timeline_urgency=timeline_urgency,
            confidentiality_level=confidentiality_level,
            budget_range=budget_range,
            brief_document=brief_document,
            consent_given=consent,
            matched_expert=preferred_expert_obj  # Save preferred expert
        )
        
        send_mail(
            subject='New client request - Kairos',
            message=f'New client request from {company} ({name}):\n\nPhone: {phone}\n\n{problem_description}\n\nEngagement type: {engagement_type}\nUrgency: {timeline_urgency}\nBudget: {budget_range or "Not specified"}\nPreferred expert: {preferred_expert_obj.user.full_name if preferred_expert_obj else "None"}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True
        )
        
        messages.success(request, 'Your request has been submitted. We will respond within 24 hours.')
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return redirect('core:home')
    
    tags = ExpertiseTag.objects.all()
    context = {
        'tags': tags,
        'preferred_expert': preferred_expert,
        'engagement_types': ClientRequest.EngagementType.choices,
        'urgency_levels': ClientRequest.UrgencyLevel.choices,
        'confidentiality_levels': ClientRequest.ConfidentialityLevel.choices,
    }
    return render(request, 'consultations/submit_request.html', context)
