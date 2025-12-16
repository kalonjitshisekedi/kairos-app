"""
Views for core functionality including home, search, legal pages, and admin dashboard.
"""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, AuditLog
from experts.models import ExpertProfile, ExpertiseTag
from consultations.models import Booking, ConciergeRequest
from payments.models import Payment


def home(request):
    verified_experts = ExpertProfile.objects.filter(
        verification_status='verified',
        is_publicly_listed=True
    ).select_related('user').order_by('-average_rating')[:6]
    
    discipline_tags = ExpertiseTag.objects.filter(tag_type='discipline')[:12]
    
    context = {
        'experts': verified_experts,
        'tags': discipline_tags,
    }
    return render(request, 'core/home.html', context)


def search(request):
    query = request.GET.get('q', '')
    
    experts = ExpertProfile.objects.filter(
        verification_status='verified',
        is_publicly_listed=True
    ).select_related('user')
    
    if query:
        experts = experts.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(headline__icontains=query) |
            Q(bio__icontains=query) |
            Q(expertise_tags__name__icontains=query)
        ).distinct()
    
    paginator = Paginator(experts, 12)
    page = request.GET.get('page')
    experts = paginator.get_page(page)
    
    return render(request, 'core/search.html', {'experts': experts, 'query': query})


def terms(request):
    return render(request, 'core/terms.html')


def privacy(request):
    return render(request, 'core/privacy.html')


def acceptable_use(request):
    return render(request, 'core/acceptable_use.html')


def how_it_works(request):
    return render(request, 'core/how_it_works.html')


def why_businesses(request):
    return render(request, 'core/why_businesses.html')


def why_kairos(request):
    return render(request, 'core/why_kairos.html')


def expertise(request):
    return render(request, 'core/expertise.html')


def contact(request):
    from .forms import ContactInquiryForm
    
    if request.method == 'POST':
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                event_type=AuditLog.EventType.ADMIN_ACTION,
                description=f'Contact inquiry submitted: {inquiry.name} ({inquiry.email})',
                ip_address=request.META.get('REMOTE_ADDR'),
                metadata={
                    'inquiry_id': str(inquiry.id),
                    'inquiry_type': inquiry.inquiry_type,
                    'popia_consent': inquiry.popia_consent
                }
            )
            messages.success(request, 'Thank you for your inquiry. Our team will be in touch within 24-48 hours.')
            return redirect('core:contact')
    else:
        form = ContactInquiryForm()
    
    return render(request, 'core/contact.html', {'form': form})


@staff_member_required
def admin_dashboard(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    pending_verifications = ExpertProfile.objects.filter(
        verification_status='pending'
    ).select_related('user').order_by('-verification_submitted_at')
    
    pending_concierge = ConciergeRequest.objects.filter(
        status='pending'
    ).select_related('client').order_by('-created_at')
    
    upcoming_sessions = Booking.objects.filter(
        status__in=['scheduled', 'accepted'],
        scheduled_start__gte=now
    ).select_related('client', 'expert__user').order_by('scheduled_start')[:10]
    
    disputed_bookings = Booking.objects.filter(
        status='disputed'
    ).select_related('client', 'expert__user')
    
    total_users = User.objects.count()
    total_experts = ExpertProfile.objects.filter(verification_status='verified').count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(
        status='completed',
        paid_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    recent_bookings = Booking.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    context = {
        'pending_verifications': pending_verifications,
        'pending_concierge': pending_concierge,
        'upcoming_sessions': upcoming_sessions,
        'disputed_bookings': disputed_bookings,
        'total_users': total_users,
        'total_experts': total_experts,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'core/admin_dashboard.html', context)


@staff_member_required
def admin_verify_expert(request, pk):
    expert = get_object_or_404(ExpertProfile, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            expert.verification_status = 'verified'
            expert.is_publicly_listed = True
            expert.verification_reviewed_at = timezone.now()
            expert.verification_reviewed_by = request.user
            expert.verification_notes = notes
            expert.save()
            
            AuditLog.objects.create(
                user=request.user,
                event_type=AuditLog.EventType.VERIFICATION_STATUS_CHANGED,
                description=f'Expert {expert.user.email} verified',
                metadata={'expert_id': str(expert.id)}
            )
            
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                subject='Your Kairos expert profile has been verified',
                message='Congratulations! Your expert profile has been verified and is now publicly visible.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[expert.user.email],
                fail_silently=True
            )
            
            messages.success(request, f'Expert {expert.user.full_name} has been verified.')
        
        elif action == 'needs_changes':
            expert.verification_status = 'needs_changes'
            expert.verification_reviewed_at = timezone.now()
            expert.verification_reviewed_by = request.user
            expert.verification_notes = notes
            expert.save()
            
            AuditLog.objects.create(
                user=request.user,
                event_type=AuditLog.EventType.VERIFICATION_STATUS_CHANGED,
                description=f'Expert {expert.user.email} needs changes',
                metadata={'expert_id': str(expert.id), 'notes': notes}
            )
            
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                subject='Changes needed for your Kairos expert profile',
                message=f'Your expert profile needs some changes before it can be verified:\n\n{notes}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[expert.user.email],
                fail_silently=True
            )
            
            messages.warning(request, f'Expert {expert.user.full_name} has been asked to make changes.')
        
        elif action == 'reject':
            expert.verification_status = 'rejected'
            expert.verification_reviewed_at = timezone.now()
            expert.verification_reviewed_by = request.user
            expert.verification_notes = notes
            expert.save()
            
            AuditLog.objects.create(
                user=request.user,
                event_type=AuditLog.EventType.VERIFICATION_STATUS_CHANGED,
                description=f'Expert {expert.user.email} rejected',
                metadata={'expert_id': str(expert.id), 'notes': notes}
            )
            
            messages.error(request, f'Expert {expert.user.full_name} has been rejected.')
        
        return redirect('core:admin_dashboard')
    
    context = {
        'expert': expert,
        'documents': expert.verification_documents.all(),
    }
    return render(request, 'core/admin_verify_expert.html', context)


@staff_member_required
def admin_match_concierge(request, pk):
    concierge = get_object_or_404(ConciergeRequest, pk=pk)
    
    if request.method == 'POST':
        expert_id = request.POST.get('expert_id')
        
        if expert_id:
            expert = get_object_or_404(ExpertProfile, pk=expert_id)
            concierge.matched_expert = expert
            concierge.matched_by = request.user
            concierge.matched_at = timezone.now()
            concierge.status = 'matched'
            concierge.admin_notes = request.POST.get('admin_notes', '')
            concierge.save()
            
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                subject='We found an expert for you - Kairos',
                message=f'We have matched you with {expert.user.full_name}. Please log in to book a consultation.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[concierge.client.email],
                fail_silently=True
            )
            
            messages.success(request, 'Concierge request matched with expert.')
            return redirect('core:admin_dashboard')
    
    experts = ExpertProfile.objects.filter(
        verification_status='verified',
        is_publicly_listed=True
    ).select_related('user')
    
    context = {
        'concierge': concierge,
        'experts': experts,
    }
    return render(request, 'core/admin_match_concierge.html', context)


@staff_member_required
def admin_audit_log(request):
    logs = AuditLog.objects.select_related('user').order_by('-created_at')
    
    event_type = request.GET.get('event_type')
    if event_type:
        logs = logs.filter(event_type=event_type)
    
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    context = {
        'logs': logs,
        'event_types': AuditLog.EventType.choices,
        'selected_type': event_type,
    }
    return render(request, 'core/admin_audit_log.html', context)
