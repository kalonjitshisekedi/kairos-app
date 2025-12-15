"""
URL configuration for availability app.
"""
from django.urls import path
from . import views

app_name = 'availability'

urlpatterns = [
    path('manage/', views.manage_availability, name='manage'),
]
