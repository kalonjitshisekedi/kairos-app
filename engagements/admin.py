"""
Admin configuration for engagements app.
"""
from django.contrib import admin
from .models import ClientRequest, ExpertMatch, Engagement, ProgressEvent


@admin.register(ClientRequest)
class ClientRequestAdmin(admin.ModelAdmin):
    list_display = ['organisation_name', 'client', 'engagement_type', 'urgency', 'status', 'created_at']
    list_filter = ['status', 'engagement_type', 'urgency', 'confidentiality_level', 'created_at']
    search_fields = ['organisation_name', 'client__email', 'brief']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Client details', {'fields': ('client', 'organisation_name', 'billing_email', 'phone')}),
        ('Request details', {'fields': ('engagement_type', 'urgency', 'brief', 'attachment', 'confidentiality_level')}),
        ('Status', {'fields': ('status', 'admin_notes')}),
        ('Metadata', {'fields': ('id', 'created_at', 'updated_at')}),
    )


@admin.register(ExpertMatch)
class ExpertMatchAdmin(admin.ModelAdmin):
    list_display = ['request', 'expert', 'status', 'proposed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['request__organisation_name', 'expert__email', 'expert__first_name', 'expert__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['request', 'expert', 'proposed_by']
    
    fieldsets = (
        ('Match details', {'fields': ('request', 'expert', 'proposed_by', 'status')}),
        ('Notes', {'fields': ('note_to_client', 'internal_note')}),
        ('Metadata', {'fields': ('id', 'created_at', 'updated_at')}),
    )


@admin.register(Engagement)
class EngagementAdmin(admin.ModelAdmin):
    list_display = ['request', 'expert', 'status', 'meeting_mode', 'scheduled_start', 'created_at']
    list_filter = ['status', 'meeting_mode', 'created_at']
    search_fields = ['request__organisation_name', 'expert__email', 'expert__first_name', 'expert__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['request', 'expert']
    
    fieldsets = (
        ('Engagement details', {'fields': ('request', 'expert', 'status')}),
        ('Scheduling', {'fields': ('scheduled_start', 'scheduled_end', 'meeting_mode', 'meeting_link')}),
        ('Notes', {'fields': ('shared_notes', 'private_expert_notes')}),
        ('Metadata', {'fields': ('id', 'created_at', 'updated_at')}),
    )


@admin.register(ProgressEvent)
class ProgressEventAdmin(admin.ModelAdmin):
    list_display = ['request', 'event_type', 'actor', 'message', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['request__organisation_name', 'message']
    readonly_fields = ['id', 'request', 'actor', 'event_type', 'message', 'created_at']
    ordering = ['-created_at']
