from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Staff authentication
    path('login/', views.staff_login, name='login'),
    path('logout/', views.staff_logout, name='logout'),
    path('register/', views.staff_registration, name='register'),
    path('profile/', views.staff_profile, name='profile'),
    
    # Customer authentication
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    path('customer/profile/', views.customer_profile, name='customer_profile'),
    
    # VIP authentication
    path('vip/login/', views.vip_login, name='vip_login'),
    path('vip/dashboard/', views.vip_dashboard, name='vip_dashboard'),
    path('vip/logout/', views.vip_logout, name='vip_logout'),
    
    # VIP dashboard pages
    path('vip/transactions/', views.vip_transactions, name='vip_transactions'),
    path('vip/cards/', views.vip_cards, name='vip_cards'),
    path('vip/cards/apply/', views.vip_card_application, name='vip_card_application'),
    path('vip/transfer/local/', views.vip_transfer_local, name='vip_transfer_local'),
    path('vip/transfer/international/', views.vip_transfer_international, name='vip_transfer_international'),
    path('vip/deposit/', views.vip_deposit, name='vip_deposit'),
]
