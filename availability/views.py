"""
Views for availability management.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta

from .models import AvailabilityBlock, TimeSlot, BlockedDate
from experts.models import ExpertProfile


@login_required
def manage_availability(request):
    if not request.user.is_expert:
        return redirect('accounts:dashboard')
    
    profile = get_object_or_404(ExpertProfile, user=request.user)
    blocks = AvailabilityBlock.objects.filter(expert=profile)
    blocked_dates = BlockedDate.objects.filter(expert=profile, date__gte=timezone.now().date())
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_block':
            day = int(request.POST.get('day_of_week'))
            start = request.POST.get('start_time')
            end = request.POST.get('end_time')
            AvailabilityBlock.objects.get_or_create(
                expert=profile,
                day_of_week=day,
                start_time=start,
                end_time=end,
                defaults={'is_active': True}
            )
            messages.success(request, 'Availability block added.')
            generate_time_slots_for_expert(profile)
        
        elif action == 'delete_block':
            block_id = request.POST.get('block_id')
            AvailabilityBlock.objects.filter(pk=block_id, expert=profile).delete()
            messages.success(request, 'Availability block removed.')
        
        elif action == 'block_date':
            date_str = request.POST.get('date')
            reason = request.POST.get('reason', '')
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            BlockedDate.objects.get_or_create(
                expert=profile,
                date=date,
                defaults={'reason': reason}
            )
            TimeSlot.objects.filter(
                expert=profile,
                start_datetime__date=date,
                status='available'
            ).update(status='blocked')
            messages.success(request, 'Date blocked.')
        
        elif action == 'unblock_date':
            date_id = request.POST.get('date_id')
            BlockedDate.objects.filter(pk=date_id, expert=profile).delete()
            messages.success(request, 'Date unblocked.')
        
        return redirect('availability:manage')
    
    context = {
        'profile': profile,
        'blocks': blocks,
        'blocked_dates': blocked_dates,
        'days': AvailabilityBlock.DayOfWeek.choices,
    }
    return render(request, 'availability/manage.html', context)


def generate_time_slots_for_expert(profile, days_ahead=30):
    today = timezone.now().date()
    blocks = AvailabilityBlock.objects.filter(expert=profile, is_active=True)
    blocked_dates = set(BlockedDate.objects.filter(
        expert=profile,
        date__gte=today,
        date__lte=today + timedelta(days=days_ahead)
    ).values_list('date', flat=True))
    
    for day_offset in range(days_ahead):
        date = today + timedelta(days=day_offset)
        if date in blocked_dates:
            continue
        
        day_of_week = date.weekday()
        day_blocks = blocks.filter(day_of_week=day_of_week)
        
        for block in day_blocks:
            start_dt = timezone.make_aware(datetime.combine(date, block.start_time))
            end_dt = timezone.make_aware(datetime.combine(date, block.end_time))
            
            current = start_dt
            while current < end_dt:
                slot_end = current + timedelta(minutes=30)
                if slot_end > end_dt:
                    break
                
                TimeSlot.objects.get_or_create(
                    expert=profile,
                    start_datetime=current,
                    defaults={
                        'end_datetime': slot_end,
                        'status': 'available'
                    }
                )
                current = slot_end


def get_available_slots(request, expert_id):
    profile = get_object_or_404(ExpertProfile, pk=expert_id)
    
    date_str = request.GET.get('date')
    duration = int(request.GET.get('duration', 60))
    
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end = start + timedelta(days=1)
    else:
        start = timezone.now()
        end = start + timedelta(days=7)
    
    slots = TimeSlot.objects.filter(
        expert=profile,
        status='available',
        start_datetime__gte=start,
        start_datetime__lt=end
    ).order_by('start_datetime')
    
    consecutive_slots_needed = duration // 30
    available_slots = []
    
    for i, slot in enumerate(slots):
        if i + consecutive_slots_needed > len(slots):
            break
        
        is_consecutive = True
        for j in range(1, consecutive_slots_needed):
            expected_start = slot.start_datetime + timedelta(minutes=30 * j)
            if slots[i + j].start_datetime != expected_start:
                is_consecutive = False
                break
            if slots[i + j].status != 'available':
                is_consecutive = False
                break
        
        if is_consecutive:
            available_slots.append({
                'id': str(slot.id),
                'start': slot.start_datetime.isoformat(),
                'end': (slot.start_datetime + timedelta(minutes=duration)).isoformat(),
                'display': slot.start_datetime.strftime('%H:%M'),
            })
    
    return JsonResponse({'slots': available_slots})
