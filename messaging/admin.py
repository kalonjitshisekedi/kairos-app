"""
Admin configuration for messaging app.
"""
from django.contrib import admin
from .models import MessageThread, Message


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ['booking', 'created_at', 'updated_at']
    search_fields = ['booking__id']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['thread', 'sender', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['sender__email', 'content']
