from django.urls import path
from . import frontend_views

app_name = 'frontend'

urlpatterns = [
    # Public landing page
    path('', frontend_views.landing_page, name='landing_page'),
    
    # Staff-only pages (require authentication)
    path('dashboard/', frontend_views.dashboard, name='dashboard'),
    path('create/', frontend_views.create_delivery_page, name='create_delivery'),
    path('where-is-my-parcel/', frontend_views.where_is_my_parcel, name='where_is_my_parcel'),
    path('tracking-status-guide/', frontend_views.tracking_status_guide, name='tracking_status_guide'),
    path('calculate-cost/', frontend_views.calculate_cost, name='calculate_cost'),
    
    # Public tracking page (no authentication required)
    path('track/<str:tracking_number>/<str:tracking_secret>/',
         frontend_views.tracking_page, name='track_delivery'),
]
