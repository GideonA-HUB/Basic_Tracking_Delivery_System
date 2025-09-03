from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'investments'

# API Router
router = DefaultRouter()
router.register(r'categories', views.InvestmentCategoryViewSet)
router.register(r'items', views.InvestmentItemViewSet)
router.register(r'investments', views.UserInvestmentViewSet, basename='user-investment')
router.register(r'transactions', views.InvestmentTransactionViewSet, basename='investment-transaction')

# URL patterns
urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/summary/', views.InvestmentSummaryView.as_view(), name='investment-summary'),
    
    # Frontend views
    path('', views.investment_marketplace, name='investment-marketplace'),
    path('dashboard/', views.investment_dashboard, name='investment-dashboard'),
    path('portfolio/', views.user_portfolio, name='user-portfolio'),
    path('item/<int:item_id>/', views.investment_item_detail, name='investment-item-detail'),
    
    # Add Funds functionality
    path('add-funds/', views.add_funds, name='add-funds'),
    path('payment-status/<int:transaction_id>/', views.payment_status, name='payment-status'),
    
    # Investment flow
    path('invest/<int:item_id>/<str:investment_type>/', views.invest_in_item, name='invest-in-item'),
    path('investment/payment-details/<int:transaction_id>/', views.investment_payment_details, name='investment-payment-details'),
    path('investment/success/<int:transaction_id>/', views.investment_success, name='investment-success'),
    path('investment/cancel/<int:transaction_id>/', views.investment_cancel, name='investment-cancel'),
    
    # Test view
    path('test/', views.investment_test, name='investment-test'),
    path('debug/', views.test_marketplace_debug, name='test-marketplace-debug'),
    
    # Admin views
    path('admin/management/', views.admin_investment_management, name='admin-investment-management'),
    path('admin/categories/', views.admin_manage_categories, name='admin-manage-categories'),
    path('admin/items/', views.admin_manage_items, name='admin-manage-items'),
    path('admin/categories/add/', views.admin_add_category, name='admin-add-category'),
    path('admin/items/add/', views.admin_add_item, name='admin-add-item'),
    
    # NOWPayments webhook
    path('webhook/', views.nowpayments_webhook, name='nowpayments-webhook'),
    
    # NOWPayments Payment URLs
    path('api/payments/ipn/', views.nowpayments_ipn_webhook, name='nowpayments-ipn'),
    path('api/payments/membership/create/', views.create_membership_payment, name='create-membership-payment'),
    path('api/payments/<str:payment_id>/status/', views.get_payment_status, name='get-payment-status'),
    path('api/payments/list/', views.user_payments_list, name='user-payments-list'),
    path('api/membership/status/', views.check_membership_status, name='check-membership-status'),
    path('api/investment-payment/<int:transaction_id>/status/', views.check_investment_payment_status, name='check-investment-payment-status'),
    
    # Membership Payment Page
    path('membership/payment/', views.membership_payment_view, name='membership-payment'),
    
    # Production database fix
    path('fix-production-db/', views.fix_production_database_view, name='fix-production-db'),
]
