"""
Admin configuration for experts app.
"""
from django.contrib import admin
from .models import ExpertProfile, ExpertiseTag, Publication, Patent, NotableProject, VerificationDocument, ExpertApplication


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'verification_status', 'privacy_level', 'is_featured', 'years_experience', 'total_consultations']
    list_filter = ['verification_status', 'privacy_level', 'is_featured', 'is_publicly_listed', 'project_work_available']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'headline']
    filter_horizontal = ['expertise_tags']
    readonly_fields = ['total_consultations', 'total_earnings', 'average_rating', 'total_reviews']
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile', {
            'fields': ('headline', 'bio', 'pronouns', 'affiliation', 'location', 'timezone', 'languages', 'avatar')
        }),
        ('Experience', {
            'fields': ('years_experience', 'senior_roles', 'sector_expertise', 'expertise_tags', 'orcid_id')
        }),
        ('Visibility', {
            'fields': ('privacy_level', 'is_publicly_listed', 'is_featured')
        }),
        ('Status', {
            'fields': ('verification_status', 'verification_submitted_at', 'verification_reviewed_at', 'verification_reviewed_by', 'verification_notes')
        }),
        ('Internal pricing (confidential)', {
            'fields': ('internal_rate', 'expert_payout_rate'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_consultations', 'total_earnings', 'average_rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExpertApplication)
class ExpertApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'years_experience', 'status', 'created_at']
    list_filter = ['status', 'years_experience']
    search_fields = ['full_name', 'email', 'expertise_areas']
    readonly_fields = ['created_at']


@admin.register(ExpertiseTag)
class ExpertiseTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'tag_type']
    list_filter = ['tag_type']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'expert', 'journal', 'year']
    search_fields = ['title', 'expert__user__email']


@admin.register(Patent)
class PatentAdmin(admin.ModelAdmin):
    list_display = ['title', 'expert', 'patent_number', 'year']
    search_fields = ['title', 'patent_number']


@admin.register(NotableProject)
class NotableProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'expert', 'year']
    search_fields = ['title']


@admin.register(VerificationDocument)
class VerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ['expert', 'document_type', 'uploaded_at']
    list_filter = ['document_type']
    search_fields = ['expert__user__email']
