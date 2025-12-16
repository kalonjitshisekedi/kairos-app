"""
Admin configuration for consultations app.
"""
from django.contrib import admin
from .models import Booking, BookingNote, BookingAttachment, Review, ExpertClientRating, ConciergeRequest, ClientRequest


@admin.register(ClientRequest)
class ClientRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'engagement_type', 'status', 'timeline_urgency', 'matched_expert', 'created_at']
    list_filter = ['status', 'engagement_type', 'timeline_urgency', 'confidentiality_level']
    search_fields = ['name', 'company', 'email', 'problem_description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Client details', {
            'fields': ('name', 'company', 'email', 'phone', 'client')
        }),
        ('Request details', {
            'fields': ('problem_description', 'engagement_type', 'timeline_urgency', 'confidentiality_level', 'budget_range', 'preferred_expertise')
        }),
        ('Brief document', {
            'fields': ('brief_document', 'consent_given')
        }),
        ('Matching', {
            'fields': ('status', 'matched_expert', 'matched_by', 'matched_at', 'internal_priority')
        }),
        ('Pricing (confidential)', {
            'fields': ('proposed_price', 'expert_payout'),
            'classes': ('collapse',)
        }),
        ('Billing', {
            'fields': ('billing_email', 'organisation_name', 'po_number', 'invoice_status')
        }),
        ('Admin notes', {
            'fields': ('admin_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ['preferred_expertise']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'expert', 'service_type', 'status', 'scheduled_start', 'amount']
    list_filter = ['status', 'service_type', 'created_at']
    search_fields = ['client__email', 'expert__user__email']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'completed_at']
    fieldsets = (
        ('Engagement details', {
            'fields': ('client', 'expert', 'client_request', 'service_type', 'scope', 'duration_description')
        }),
        ('Schedule', {
            'fields': ('scheduled_start', 'scheduled_end', 'jitsi_room_id', 'external_meeting_link')
        }),
        ('Status', {
            'fields': ('status', 'problem_statement')
        }),
        ('Pricing (confidential)', {
            'fields': ('amount', 'expert_payout', 'currency'),
            'classes': ('collapse',)
        }),
    )


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
