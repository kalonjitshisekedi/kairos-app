"""
Blog views for Kairos insight desk.
"""
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .models import BlogPost


def blog_index(request):
    posts = BlogPost.objects.filter(
        is_published=True,
        published_at__isnull=False
    ).order_by('-published_at')
    
    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    return render(request, 'blog/index.html', {'posts': posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    
    if not post.is_published:
        raise Http404('Post not found')
    
    related_posts = BlogPost.objects.filter(
        is_published=True,
        published_at__isnull=False
    ).exclude(id=post.id).order_by('-published_at')[:3]
    
    return render(request, 'blog/detail.html', {
        'post': post,
        'related_posts': related_posts
    })
