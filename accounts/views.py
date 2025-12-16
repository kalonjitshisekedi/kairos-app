"""
Views for user authentication and account management.
"""
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from .forms import SignUpForm, LoginForm, ProfileUpdateForm, DeletionRequestForm, CustomPasswordResetForm, CustomSetPasswordForm
from .models import AuditLog

User = get_user_model()


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        user = form.save()
        AuditLog.objects.create(
            user=user,
            event_type=AuditLog.EventType.USER_CREATED,
            description=f'User created with role: {user.role}',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        login(self.request, user)
        messages.success(self.request, 'Welcome to Kairos! Your account has been created.')
        if user.role == 'expert':
            from experts.models import ExpertProfile
            ExpertProfile.objects.get_or_create(user=user)
            return redirect('experts:profile_wizard')
        return redirect('accounts:dashboard')


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            event_type=AuditLog.EventType.USER_LOGIN,
            description='User logged in',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        return response

    def get_success_url(self):
        user = self.request.user
        if user.is_admin or user.is_staff:
            return reverse_lazy('core:admin_dashboard')
        elif user.is_expert:
            return reverse_lazy('experts:dashboard')
        return reverse_lazy('accounts:dashboard')


class CustomLogoutView(LogoutView):
    next_page = 'core:home'
    http_method_names = ['get', 'post', 'options']

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                event_type=AuditLog.EventType.USER_LOGOUT,
                description='User logged out',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
        messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


@login_required
def dashboard(request):
    user = request.user
    if user.is_admin or user.is_staff:
        return redirect('core:admin_dashboard')
    elif user.is_expert:
        return redirect('experts:dashboard')
    
    from consultations.models import Booking, ConciergeRequest
    bookings = Booking.objects.filter(client=user).exclude(status='archived').order_by('-created_at')[:10]
    concierge_requests = ConciergeRequest.objects.filter(client=user).order_by('-created_at')[:5]
    upcoming_sessions = Booking.objects.filter(
        client=user,
        status__in=['scheduled', 'accepted'],
        scheduled_start__gte=timezone.now()
    ).order_by('scheduled_start')[:5]
    
    context = {
        'bookings': bookings,
        'concierge_requests': concierge_requests,
        'upcoming_sessions': upcoming_sessions,
    }
    return render(request, 'accounts/client_dashboard.html', context)


@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                event_type=AuditLog.EventType.PROFILE_UPDATED,
                description='Profile updated',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:profile_settings')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile_settings.html', {'form': form})


@login_required
def request_deletion(request):
    if request.method == 'POST':
        form = DeletionRequestForm(request.user, request.POST)
        if form.is_valid():
            request.user.deletion_requested = True
            request.user.deletion_requested_date = timezone.now()
            request.user.save()
            AuditLog.objects.create(
                user=request.user,
                event_type=AuditLog.EventType.DELETION_REQUESTED,
                description=f'Deletion requested. Reason: {form.cleaned_data.get("reason", "Not provided")}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            send_mail(
                subject='Account deletion request - Kairos',
                message=f'User {request.user.email} has requested account deletion.\n\nReason: {form.cleaned_data.get("reason", "Not provided")}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True
            )
            messages.info(request, 'Your deletion request has been submitted. Our team will process it within 30 days.')
            return redirect('accounts:dashboard')
    else:
        form = DeletionRequestForm(request.user)
    return render(request, 'accounts/request_deletion.html', {'form': form})
