"""
URL configuration for Kairos project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('experts/', include('experts.urls')),
    path('availability/', include('availability.urls')),
    path('consultations/', include('consultations.urls')),
    path('messaging/', include('messaging.urls')),
    path('payments/', include('payments.urls')),
    path('api/', include('availability.api_urls')),
    path('blog/', include('blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
