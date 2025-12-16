"""
Blog models for Kairos insight desk.
"""
import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class BlogPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    excerpt = models.TextField(max_length=500, help_text='Brief summary for listing pages')
    content = models.TextField(help_text='Main content (HTML allowed)')
    author_name = models.CharField(max_length=200, default='Kairos Team')
    reading_time_minutes = models.PositiveIntegerField(default=5, help_text='Estimated reading time')
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_post'
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Blog post'
        verbose_name_plural = 'Blog posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_visible(self):
        return self.is_published and self.published_at is not None
