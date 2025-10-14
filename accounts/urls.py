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
    
    # Individual transfer method URLs
    path('vip/transfer/wire/', views.vip_transfer_wire, name='vip_transfer_wire'),
    path('vip/transfer/cryptocurrency/', views.vip_transfer_cryptocurrency, name='vip_transfer_cryptocurrency'),
    path('vip/transfer/paypal/', views.vip_transfer_paypal, name='vip_transfer_paypal'),
    path('vip/transfer/wise/', views.vip_transfer_wise, name='vip_transfer_wise'),
    path('vip/transfer/cashapp/', views.vip_transfer_cashapp, name='vip_transfer_cashapp'),
    path('vip/transfer/skrill/', views.vip_transfer_skrill, name='vip_transfer_skrill'),
    path('vip/transfer/venmo/', views.vip_transfer_venmo, name='vip_transfer_venmo'),
    path('vip/transfer/zelle/', views.vip_transfer_zelle, name='vip_transfer_zelle'),
    path('vip/transfer/revolut/', views.vip_transfer_revolut, name='vip_transfer_revolut'),
    path('vip/transfer/alipay/', views.vip_transfer_alipay, name='vip_transfer_alipay'),
    path('vip/transfer/wechat/', views.vip_transfer_wechat, name='vip_transfer_wechat'),
    path('vip/deposit/', views.vip_deposit, name='vip_deposit'),
    
    # VIP loan services
    path('vip/loans/', views.vip_loan_services, name='vip_loan_services'),
    path('vip/loans/apply/', views.vip_loan_application, name='vip_loan_application'),
    path('vip/loans/faqs/', views.vip_loan_faqs, name='vip_loan_faqs'),
    
    # VIP IRS Tax Refund services
    path('vip/irs-tax-refund/', views.vip_irs_tax_refund, name='vip_irs_tax_refund'),
    path('vip/irs-tax-refund/status/<str:reference_number>/', views.vip_irs_tax_refund_status, name='vip_irs_tax_refund_status'),
    path('vip/irs-tax-refund/history/', views.vip_irs_tax_refund_history, name='vip_irs_tax_refund_history'),
]
