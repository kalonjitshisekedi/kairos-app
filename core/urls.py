"""
URL configuration for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('acceptable-use/', views.acceptable_use, name='acceptable_use'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('operations/', views.admin_dashboard, name='admin_dashboard'),
    path('operations/verify/<uuid:pk>/', views.admin_verify_expert, name='admin_verify_expert'),
    path('operations/concierge/<uuid:pk>/', views.admin_match_concierge, name='admin_match_concierge'),
    path('operations/audit-log/', views.admin_audit_log, name='admin_audit_log'),
]
