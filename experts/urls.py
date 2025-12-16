"""
URL configuration for experts app.
"""
from django.urls import path
from . import views

app_name = 'experts'

urlpatterns = [
    path('', views.expert_directory, name='directory'),
    path('careers/', views.careers, name='careers'),
    path('join/', views.join_as_expert, name='join'),
    path('profile/<uuid:pk>/', views.expert_profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('wizard/', views.profile_wizard, name='profile_wizard'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('publications/', views.manage_publications, name='manage_publications'),
    path('publications/<uuid:pk>/delete/', views.delete_publication, name='delete_publication'),
]
