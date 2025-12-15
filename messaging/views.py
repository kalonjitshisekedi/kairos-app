"""
Views for messaging.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import MessageThread, Message


@login_required
def thread_detail(request, pk):
    thread = get_object_or_404(MessageThread.objects.select_related('booking__client', 'booking__expert__user'), pk=pk)
    booking = thread.booking
    
    if not (request.user == booking.client or request.user == booking.expert.user):
        return HttpResponseForbidden()
    
    thread.messages.exclude(sender=request.user).update(is_read=True, read_at=timezone.now())
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                thread=thread,
                sender=request.user,
                content=content
            )
            thread.save()
            
            if request.user == booking.client:
                recipient = booking.expert.user
            else:
                recipient = booking.client
            
            send_mail(
                subject=f'New message - Kairos',
                message=f'You have a new message from {request.user.full_name}:\n\n{content[:200]}...\n\nLog in to reply.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=True
            )
            
            messages.success(request, 'Message sent.')
        return redirect('messaging:thread', pk=pk)
    
    thread_messages = thread.messages.order_by('created_at')
    
    context = {
        'thread': thread,
        'booking': booking,
        'messages_list': thread_messages,
    }
    return render(request, 'messaging/thread.html', context)


@login_required
def my_messages(request):
    from consultations.models import Booking
    
    if request.user.is_expert:
        try:
            profile = request.user.expert_profile
            bookings = Booking.objects.filter(expert=profile)
        except:
            bookings = Booking.objects.none()
    else:
        bookings = Booking.objects.filter(client=request.user)
    
    threads = MessageThread.objects.filter(booking__in=bookings).select_related('booking__client', 'booking__expert__user').order_by('-updated_at')
    
    return render(request, 'messaging/my_messages.html', {'threads': threads})
