"""
URL configuration for messaging app.
"""
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.my_messages, name='my_messages'),
    path('thread/<uuid:pk>/', views.thread_detail, name='thread'),
]
