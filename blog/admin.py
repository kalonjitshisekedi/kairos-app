"""
Blog admin configuration.
"""
from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_name', 'is_published', 'published_at', 'reading_time_minutes']
    list_filter = ['is_published', 'published_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    date_hierarchy = 'published_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Publishing', {
            'fields': ('author_name', 'reading_time_minutes', 'is_published', 'published_at')
        }),
    )
