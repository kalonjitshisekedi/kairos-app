"""
API URL configuration for availability.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('experts/<uuid:expert_id>/slots/', views.get_available_slots, name='get_slots'),
]
