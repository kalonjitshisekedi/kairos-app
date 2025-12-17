"""
Access control decorators for Kairos platform.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def verified_client_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_admin:
            return view_func(request, *args, **kwargs)
        if user.role != 'client':
            messages.error(request, 'This feature is only available to clients.')
            return redirect('core:home')
        if user.client_status != 'verified':
            messages.error(request, 'Your account is pending verification. Please wait for approval to access this feature.')
            return redirect('accounts:client_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def active_expert_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_admin:
            return view_func(request, *args, **kwargs)
        if user.role != 'expert':
            messages.error(request, 'This feature is only available to experts.')
            return redirect('core:home')
        if user.expert_status not in ['vetted', 'active']:
            messages.error(request, 'Your expert profile is not yet active. Please wait for approval.')
            return redirect('experts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


class VerifiedClientRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_admin:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role != 'client':
            messages.error(request, 'This feature is only available to clients.')
            return redirect('core:home')
        if request.user.client_status != 'verified':
            messages.error(request, 'Your account is pending verification. Please wait for approval to access this feature.')
            return redirect('accounts:client_dashboard')
        return super().dispatch(request, *args, **kwargs)


class ActiveExpertRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_admin:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role != 'expert':
            messages.error(request, 'This feature is only available to experts.')
            return redirect('core:home')
        if request.user.expert_status not in ['vetted', 'active']:
            messages.error(request, 'Your expert profile is not yet active. Please wait for approval.')
            return redirect('experts:dashboard')
        return super().dispatch(request, *args, **kwargs)
