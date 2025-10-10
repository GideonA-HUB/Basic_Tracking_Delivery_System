from django.urls import path
from . import views

app_name = 'vip_members'

urlpatterns = [
    # VIP Application and Access Control
    path('', views.vip_login_redirect, name='index'),
    path('apply/', views.vip_application, name='apply'),
    path('application-status/', views.application_status, name='application_status'),
    
    # VIP Dashboard (only for approved members)
    path('dashboard/', views.vip_dashboard, name='dashboard'),
    
    # VIP Profile and Settings
    path('profile/', views.vip_profile, name='profile'),
    
    # VIP Benefits
    path('benefits/', views.vip_benefits, name='benefits'),
    
    # VIP Support
    path('support/', views.vip_support, name='support'),
    
    # VIP Activities
    path('activities/', views.vip_activities, name='activities'),
    
    # AJAX endpoints
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Public pages
    path('membership-info/', views.vip_membership_info, name='membership_info'),
]
