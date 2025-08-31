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
    
    # Test view
    path('test/', views.investment_test, name='investment-test'),
    
    # Admin views
    path('admin/management/', views.admin_investment_management, name='admin-investment-management'),
    path('admin/categories/', views.admin_manage_categories, name='admin-manage-categories'),
    path('admin/items/', views.admin_manage_items, name='admin-manage-items'),
    path('admin/categories/add/', views.admin_add_category, name='admin-add-category'),
    path('admin/items/add/', views.admin_add_item, name='admin-add-item'),
    
    # NOWPayments webhook
    path('webhook/', views.nowpayments_webhook, name='nowpayments-webhook'),
]
