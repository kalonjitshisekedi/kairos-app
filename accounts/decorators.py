"""
Custom decorators for access control.
"""
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def verified_client_required(view_func):
    """
    Decorator that requires user to be authenticated with verified client status.
    
    Redirects to request form with message if:
    - User is not authenticated
    - User's client_status is not 'verified'
    
    Admins and experts bypass this check.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'Please log in or submit a request to access expert information.')
            return redirect('consultations:submit_request')
        
        if request.user.is_admin or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if request.user.is_expert:
            return view_func(request, *args, **kwargs)
        
        from accounts.models import User
        if request.user.client_status != User.ClientStatus.VERIFIED:
            messages.warning(request, 'Your account must be verified before accessing expert information.')
            return redirect('consultations:submit_request')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
