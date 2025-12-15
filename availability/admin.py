"""
Admin configuration for availability app.
"""
from django.contrib import admin
from .models import AvailabilityBlock, TimeSlot, BlockedDate


@admin.register(AvailabilityBlock)
class AvailabilityBlockAdmin(admin.ModelAdmin):
    list_display = ['expert', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']
    search_fields = ['expert__user__email']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['expert', 'start_datetime', 'end_datetime', 'status']
    list_filter = ['status', 'start_datetime']
    search_fields = ['expert__user__email']
    date_hierarchy = 'start_datetime'


@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ['expert', 'date', 'reason']
    list_filter = ['date']
    search_fields = ['expert__user__email', 'reason']
