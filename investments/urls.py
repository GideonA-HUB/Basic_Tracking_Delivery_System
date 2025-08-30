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
    
    # Admin views
    path('admin/management/', views.admin_investment_management, name='admin-investment-management'),
    
    # NOWPayments webhook
    path('webhook/', views.nowpayments_webhook, name='nowpayments-webhook'),
]
