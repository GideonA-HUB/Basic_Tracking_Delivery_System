from django.urls import path
from . import frontend_views

app_name = 'frontend'

urlpatterns = [
    # Public landing page (now using Figma design)
    path('', frontend_views.landing_page_figma, name='landing_page'),
    
    # Original landing page (moved to /original/)
    path('original/', frontend_views.landing_page, name='landing_page_original'),
    
    # Tracking search endpoint
    path('search-tracking/', frontend_views.search_tracking_number, name='search_tracking'),
    
    # Staff-only pages (require authentication)
    path('dashboard/', frontend_views.dashboard, name='dashboard'),
    path('create/', frontend_views.create_delivery_page, name='create_delivery'),
    path('where-is-my-parcel/', frontend_views.where_is_my_parcel, name='where_is_my_parcel'),
    path('tracking-status-guide/', frontend_views.tracking_status_guide, name='tracking_status_guide'),
    path('calculate-cost/', frontend_views.calculate_cost, name='calculate_cost'),
    
    # Public tracking page (no authentication required)
    path('track/<str:tracking_number>/<str:tracking_secret>/',
         frontend_views.tracking_page, name='track_delivery'),
    
    # Newsletter subscription endpoint
    path('newsletter/subscribe/', frontend_views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # FAQ page
    path('faqs/', frontend_views.faqs, name='faqs'),
]
