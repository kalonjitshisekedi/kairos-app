"""
URL configuration for consultations app.
"""
from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('book/<uuid:expert_id>/', views.create_booking, name='create_booking'),
    path('booking/<uuid:pk>/', views.booking_detail, name='booking_detail'),
    path('booking/<uuid:pk>/session/', views.session_room, name='session_room'),
    path('booking/<uuid:pk>/note/', views.add_note, name='add_note'),
    path('booking/<uuid:pk>/upload/', views.upload_attachment, name='upload_attachment'),
    path('booking/<uuid:pk>/complete/', views.mark_complete, name='mark_complete'),
    path('booking/<uuid:pk>/review/', views.leave_review, name='leave_review'),
    path('booking/<uuid:pk>/rate-client/', views.expert_rate_client, name='rate_client'),
    path('booking/<uuid:pk>/accept/', views.accept_booking, name='accept_booking'),
    path('booking/<uuid:pk>/decline/', views.decline_booking, name='decline_booking'),
    path('concierge/', views.create_concierge_request, name='concierge_request'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]
