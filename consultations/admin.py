"""
Admin configuration for consultations app.
"""
from django.contrib import admin
from .models import Booking, BookingNote, BookingAttachment, Review, ExpertClientRating, ConciergeRequest


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'expert', 'status', 'scheduled_start', 'duration', 'amount']
    list_filter = ['status', 'duration', 'created_at']
    search_fields = ['client__email', 'expert__user__email']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'completed_at']


@admin.register(BookingNote)
class BookingNoteAdmin(admin.ModelAdmin):
    list_display = ['booking', 'author', 'note_type', 'created_at']
    list_filter = ['note_type']
    search_fields = ['booking__id', 'author__email']


@admin.register(BookingAttachment)
class BookingAttachmentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'uploaded_by', 'filename', 'is_deliverable', 'uploaded_at']
    list_filter = ['is_deliverable']
    search_fields = ['filename']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['booking', 'reviewer', 'reviewee', 'rating', 'is_public', 'created_at']
    list_filter = ['rating', 'is_public']
    search_fields = ['reviewer__email', 'reviewee__email']


@admin.register(ExpertClientRating)
class ExpertClientRatingAdmin(admin.ModelAdmin):
    list_display = ['expert', 'client', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(ConciergeRequest)
class ConciergeRequestAdmin(admin.ModelAdmin):
    list_display = ['client', 'status', 'matched_expert', 'created_at']
    list_filter = ['status']
    search_fields = ['client__email', 'description']
