"""
Admin configuration for experts app.
"""
from django.contrib import admin
from .models import ExpertProfile, ExpertiseTag, Publication, Patent, NotableProject, VerificationDocument


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'verification_status', 'is_publicly_listed', 'total_consultations']
    list_filter = ['verification_status', 'is_publicly_listed', 'project_work_available']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'headline']
    filter_horizontal = ['expertise_tags']
    readonly_fields = ['total_consultations', 'total_earnings', 'average_rating', 'total_reviews']


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
