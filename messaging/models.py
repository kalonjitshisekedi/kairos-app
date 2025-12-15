"""
Messaging models for per-booking communication.
"""
import uuid
from django.conf import settings
from django.db import models


class MessageThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField('consultations.Booking', on_delete=models.CASCADE, related_name='message_thread')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messaging_thread'
        ordering = ['-updated_at']

    def __str__(self):
        return f'Thread for booking {self.booking_id}'

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()

    @property
    def unread_count(self):
        return self.messages.filter(is_read=False).count()


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messaging_message'
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender} at {self.created_at}'


class MessageAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='message_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messaging_attachment'

    def __str__(self):
        return self.filename
