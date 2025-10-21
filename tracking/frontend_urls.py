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
    
    # Footer pages
    path('claims/', frontend_views.claims, name='claims'),
    path('support-center/', frontend_views.support_center, name='support_center'),
    path('logistics/', frontend_views.logistics, name='logistics'),
    path('warehousing/', frontend_views.warehousing, name='warehousing'),
    path('distribution/', frontend_views.distribution, name='distribution'),
    path('customs-brokerage/', frontend_views.customs_brokerage, name='customs_brokerage'),
    
    # About section pages
    path('company-overview/', frontend_views.company_overview, name='company_overview'),
    path('leadership/', frontend_views.leadership, name='leadership'),
    path('investor-relations/', frontend_views.investor_relations, name='investor_relations'),
    path('newsroom/', frontend_views.newsroom, name='newsroom'),
    
    # Legal section pages
    path('terms/', frontend_views.terms, name='terms'),
    path('privacy/', frontend_views.privacy, name='privacy'),
    path('cookies/', frontend_views.cookies, name='cookies'),
    
    # Security section pages
    path('fraud-protection/', frontend_views.fraud_protection, name='fraud_protection'),
    path('security-center/', frontend_views.security_center, name='security_center'),
    path('report-issues/', frontend_views.report_issues, name='report_issues'),
]
