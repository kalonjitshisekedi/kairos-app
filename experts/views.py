"""
Views for expert profile management and directory.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.decorators import verified_client_required
from accounts.models import AuditLog, User
from consultations.models import Booking
from .models import ExpertProfile, ExpertiseTag, Publication, Patent, NotableProject, VerificationDocument
from .forms import (
    ExpertProfileBasicForm, ExpertProfileAvatarForm, ExpertProfileExpertiseForm,
    ExpertProfileExperienceForm, PublicationForm, PatentForm, NotableProjectForm, VerificationDocumentForm
)


@verified_client_required
def expert_directory(request):
    """Expert directory - requires verified client status.
    
    Privacy levels control visibility:
    - public: Visible to verified clients
    - semi_private: Visible to verified clients
    - private: Never shown in directory (matched by admin only)
    """
    base_query = ExpertProfile.objects.filter(
        verification_status__in=['vetted', 'active'],
        is_publicly_listed=True,
    ).select_related('user').prefetch_related('expertise_tags')
    
    is_verified_client = (
        request.user.is_authenticated and 
        request.user.is_client and 
        request.user.client_status == User.ClientStatus.VERIFIED
    )
    is_admin = request.user.is_authenticated and request.user.is_admin
    
    if is_verified_client or is_admin:
        experts = base_query.filter(privacy_level__in=['public', 'semi_private'])
    else:
        experts = base_query.filter(privacy_level='public')
    
    search = request.GET.get('search', '')
    if search:
        experts = experts.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(headline__icontains=search) |
            Q(bio__icontains=search)
        )
    
    expertise = request.GET.getlist('expertise')
    if expertise:
        experts = experts.filter(expertise_tags__slug__in=expertise).distinct()
    
    sort = request.GET.get('sort', 'rating')
    if sort == 'experience_high':
        experts = experts.order_by('-years_experience')
    else:
        experts = experts.order_by('-average_rating', '-total_reviews')
    
    paginator = Paginator(experts, 12)
    page = request.GET.get('page')
    experts = paginator.get_page(page)
    
    discipline_tags = ExpertiseTag.objects.filter(tag_type='discipline')
    
    context = {
        'experts': experts,
        'discipline_tags': discipline_tags,
        'search': search,
        'selected_expertise': expertise,
        'sort': sort,
    }
    return render(request, 'experts/directory.html', context)


def join_as_expert(request):
    """Careers page for experts with application form."""
    from .forms_application import ExpertApplicationForm
    
    if request.method == 'POST':
        form = ExpertApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save()
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                event_type=AuditLog.EventType.ADMIN_ACTION,
                description=f'Expert application submitted: {application.full_name} ({application.email})',
                ip_address=request.META.get('REMOTE_ADDR'),
                metadata={
                    'application_id': str(application.id),
                    'expertise_areas': application.expertise_areas,
                    'popia_consent': application.popia_consent,
                    'has_cv': bool(application.cv_file)
                }
            )
            messages.success(request, 'Thank you for your application! Our team will review it and contact you within 5 business days.')
            return redirect('experts:join')
    else:
        form = ExpertApplicationForm()
    
    return render(request, 'experts/join.html', {'form': form})


@verified_client_required
def careers(request):
    """Careers page with skill/expertise-based search - requires verified client status."""
    experts = ExpertProfile.objects.filter(
        verification_status__in=['vetted', 'active'],
        is_publicly_listed=True,
        privacy_level__in=['public', 'semi_private']
    ).select_related('user')
    
    skills = request.GET.get('skills', '')
    if skills:
        experts = experts.filter(
            Q(headline__icontains=skills) |
            Q(bio__icontains=skills)
        )
    
    expertise = request.GET.getlist('expertise')
    if expertise:
        experts = experts.filter(expertise_tags__slug__in=expertise).distinct()
    
    availability = request.GET.get('availability', '')
    if availability == 'project_work':
        experts = experts.filter(project_work_available=True)
    elif availability == 'available_now':
        from availability.models import TimeSlot
        available_expert_ids = TimeSlot.objects.filter(
            status='available',
            start_datetime__gte=timezone.now()
        ).values_list('expert_id', flat=True).distinct()
        experts = experts.filter(pk__in=available_expert_ids)
    
    sort = request.GET.get('sort', 'rating')
    if sort == 'reviews':
        experts = experts.order_by('-total_reviews', '-average_rating')
    elif sort == 'recent':
        experts = experts.order_by('-created_at')
    else:
        experts = experts.order_by('-average_rating', '-total_reviews')
    
    paginator = Paginator(experts, 12)
    page = request.GET.get('page')
    experts = paginator.get_page(page)
    
    discipline_tags = ExpertiseTag.objects.filter(tag_type='discipline')
    
    context = {
        'experts': experts,
        'discipline_tags': discipline_tags,
        'skills': skills,
        'selected_expertise': expertise,
        'availability': availability,
        'sort': sort,
    }
    return render(request, 'experts/careers.html', context)


@verified_client_required
def expert_profile(request, pk):
    """View expert profile - requires verified client status.
    
    Access rules:
    - public/semi_private: Visible to verified clients, owner, or admin
    - private: Visible only to owner or admin
    """
    expert = get_object_or_404(
        ExpertProfile.objects.select_related('user').prefetch_related(
            'expertise_tags', 'publications', 'patents', 'notable_projects'
        ),
        pk=pk
    )
    
    is_own_profile = request.user.is_authenticated and request.user == expert.user
    is_admin = request.user.is_authenticated and request.user.is_admin
    
    if not expert.is_publicly_listed and not (is_own_profile or is_admin):
        messages.error(request, 'This expert profile is not available.')
        return redirect('experts:directory')
    
    if expert.privacy_level == 'private' and not (is_own_profile or is_admin):
        messages.error(request, 'This expert profile is private.')
        return redirect('experts:directory')
    
    reviews = Booking.objects.filter(
        expert=expert,
        status='completed',
        review__isnull=False,
        review__is_public=True
    ).select_related('review', 'client')[:10]
    
    from availability.models import TimeSlot
    next_slots = TimeSlot.objects.filter(
        expert=expert,
        status='available',
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')[:5]
    
    avg_response_time = expert.calculate_average_response_time()
    
    context = {
        'expert': expert,
        'reviews': reviews,
        'next_slots': next_slots,
        'avg_response_time': avg_response_time,
    }
    return render(request, 'experts/profile.html', context)


@login_required
def dashboard(request):
    if not request.user.is_expert:
        return redirect('accounts:dashboard')
    
    try:
        profile = request.user.expert_profile
    except ExpertProfile.DoesNotExist:
        profile = ExpertProfile.objects.create(user=request.user)
    
    pending_requests = Booking.objects.filter(
        expert=profile,
        status='requested'
    ).order_by('-created_at')[:5]
    
    upcoming_sessions = Booking.objects.filter(
        expert=profile,
        status__in=['accepted', 'scheduled'],
        scheduled_start__gte=timezone.now()
    ).order_by('scheduled_start')[:5]
    
    recent_bookings = Booking.objects.filter(expert=profile).order_by('-created_at')[:10]
    
    from payments.models import Payment
    total_earnings = Payment.objects.filter(
        booking__expert=profile,
        status='completed'
    ).aggregate(total=Avg('amount'))['total'] or 0
    
    context = {
        'profile': profile,
        'pending_requests': pending_requests,
        'upcoming_sessions': upcoming_sessions,
        'recent_bookings': recent_bookings,
        'total_earnings': profile.total_earnings,
    }
    return render(request, 'experts/dashboard.html', context)


@login_required
def profile_wizard(request):
    if not request.user.is_expert:
        return redirect('accounts:dashboard')
    
    try:
        profile = request.user.expert_profile
    except ExpertProfile.DoesNotExist:
        profile = ExpertProfile.objects.create(user=request.user)
    
    step = request.GET.get('step', '1')
    
    if step == '1':
        form = ExpertProfileBasicForm(request.POST or None, instance=profile)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect('experts:profile_wizard') + '?step=2'
        template = 'experts/wizard/step1_basic.html'
    elif step == '2':
        form = ExpertProfileAvatarForm(request.POST or None, request.FILES or None, instance=profile)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect('experts:profile_wizard') + '?step=3'
        template = 'experts/wizard/step2_avatar.html'
    elif step == '3':
        form = ExpertProfileExpertiseForm(request.POST or None, instance=profile)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect('experts:profile_wizard') + '?step=4'
        template = 'experts/wizard/step3_expertise.html'
    elif step == '4':
        form = ExpertProfileExperienceForm(request.POST or None, instance=profile)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect('experts:profile_wizard') + '?step=5'
        template = 'experts/wizard/step4_rates.html'
    elif step == '5':
        form = VerificationDocumentForm(request.POST or None, request.FILES or None)
        if request.method == 'POST' and form.is_valid():
            doc = form.save(commit=False)
            doc.expert = profile
            doc.save()
            AuditLog.objects.create(
                user=request.user,
                event_type=AuditLog.EventType.FILE_UPLOADED,
                description=f'Verification document uploaded: {doc.get_document_type_display()}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return redirect('experts:profile_wizard') + '?step=6'
        template = 'experts/wizard/step5_verification.html'
    else:
        if profile.verification_status == 'applied':
            profile.verification_submitted_at = timezone.now()
            profile.save()
            AuditLog.objects.create(
                user=request.user,
                event_type=AuditLog.EventType.VERIFICATION_STATUS_CHANGED,
                description='Profile submitted for vetting',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, 'Your profile has been submitted for review. Our team will vet your application shortly.')
        return redirect('experts:dashboard')
    
    context = {
        'form': form,
        'profile': profile,
        'step': step,
        'total_steps': 6,
    }
    return render(request, template, context)


@login_required
def edit_profile(request):
    if not request.user.is_expert:
        return redirect('accounts:dashboard')
    
    profile = get_object_or_404(ExpertProfile, user=request.user)
    
    if request.method == 'POST':
        basic_form = ExpertProfileBasicForm(request.POST, instance=profile)
        avatar_form = ExpertProfileAvatarForm(request.POST, request.FILES, instance=profile)
        expertise_form = ExpertProfileExpertiseForm(request.POST, instance=profile)
        experience_form = ExpertProfileExperienceForm(request.POST, instance=profile)
        
        if all([basic_form.is_valid(), avatar_form.is_valid(), expertise_form.is_valid(), experience_form.is_valid()]):
            basic_form.save()
            if request.FILES.get('avatar'):
                avatar_form.save()
            expertise_form.save()
            experience_form.save()
            AuditLog.objects.create(
                user=request.user,
                event_type=AuditLog.EventType.PROFILE_UPDATED,
                description='Expert profile updated',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, 'Your profile has been updated.')
            return redirect('experts:dashboard')
    else:
        basic_form = ExpertProfileBasicForm(instance=profile)
        avatar_form = ExpertProfileAvatarForm(instance=profile)
        expertise_form = ExpertProfileExpertiseForm(instance=profile)
        experience_form = ExpertProfileExperienceForm(instance=profile)
    
    context = {
        'profile': profile,
        'basic_form': basic_form,
        'avatar_form': avatar_form,
        'expertise_form': expertise_form,
        'experience_form': experience_form,
    }
    return render(request, 'experts/edit_profile.html', context)


@login_required
def manage_publications(request):
    if not request.user.is_expert:
        return redirect('accounts:dashboard')
    
    profile = get_object_or_404(ExpertProfile, user=request.user)
    publications = profile.publications.all()
    
    if request.method == 'POST':
        form = PublicationForm(request.POST)
        if form.is_valid():
            pub = form.save(commit=False)
            pub.expert = profile
            pub.save()
            messages.success(request, 'Publication added.')
            return redirect('experts:manage_publications')
    else:
        form = PublicationForm()
    
    context = {
        'profile': profile,
        'publications': publications,
        'form': form,
    }
    return render(request, 'experts/manage_publications.html', context)


@login_required
def delete_publication(request, pk):
    if not request.user.is_expert:
        return redirect('accounts:dashboard')
    
    pub = get_object_or_404(Publication, pk=pk, expert__user=request.user)
    pub.delete()
    messages.success(request, 'Publication removed.')
    return redirect('experts:manage_publications')
