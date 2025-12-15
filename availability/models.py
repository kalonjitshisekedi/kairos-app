"""
Availability management models for experts.
"""
import uuid
from django.conf import settings
from django.db import models


class AvailabilityBlock(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expert = models.ForeignKey('experts.ExpertProfile', on_delete=models.CASCADE, related_name='availability_blocks')
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'availability_block'
        ordering = ['day_of_week', 'start_time']
        unique_together = ['expert', 'day_of_week', 'start_time', 'end_time']

    def __str__(self):
        return f'{self.expert} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}'


class TimeSlot(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        BOOKED = 'booked', 'Booked'
        BLOCKED = 'blocked', 'Blocked'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expert = models.ForeignKey('experts.ExpertProfile', on_delete=models.CASCADE, related_name='time_slots')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    booking = models.ForeignKey('consultations.Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='time_slots')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'availability_time_slot'
        ordering = ['start_datetime']

    def __str__(self):
        return f'{self.expert} - {self.start_datetime}'

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE

    @property
    def duration_minutes(self):
        return int((self.end_datetime - self.start_datetime).total_seconds() / 60)


class BlockedDate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expert = models.ForeignKey('experts.ExpertProfile', on_delete=models.CASCADE, related_name='blocked_dates')
    date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'availability_blocked_date'
        unique_together = ['expert', 'date']
        ordering = ['date']

    def __str__(self):
        return f'{self.expert} - {self.date}'
