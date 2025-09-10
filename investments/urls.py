from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import debug_views
from . import debug_env
from . import websocket_test
from . import management_views
from . import force_fetch_views

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
    path('api/price-statistics/', views.PriceStatisticsView.as_view(), name='price-statistics'),
    path('api/live-prices/', views.LivePricesView.as_view(), name='live-prices'),
    
    # Frontend views
    path('', views.investment_marketplace, name='investment-marketplace'),
    path('dashboard/', views.investment_dashboard, name='investment-dashboard'),
    path('enhanced-dashboard/', views.enhanced_dashboard, name='enhanced-dashboard'),
    path('live-dashboard/', views.live_dashboard, name='live-dashboard'),
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
    
    # NOWPayments Configuration Status (Admin only)
    path('admin/nowpayments-config/', views.nowpayments_config_status, name='nowpayments-config-status'),
    
    # Meridian Quick Access
    path('meridian-quick-access/', views.meridian_quick_access, name='meridian-quick-access'),
    
    # News System URLs
    path('news/', views.news_dashboard, name='news-dashboard'),
    path('news/article/<uuid:article_id>/', views.news_article_detail, name='news-article-detail'),
    
    # News API URLs
    path('api/news/', views.NewsAPIView.as_view(), name='news-api'),
    path('api/news/refresh/', views.NewsRefreshAPIView.as_view(), name='news-refresh'),
    path('api/news/refresh/public/', views.PublicNewsRefreshAPIView.as_view(), name='news-refresh-public'),
    path('api/news/widget/', views.NewsWidgetAPIView.as_view(), name='news-widget'),
    path('api/news/preferences/', views.NewsPreferencesAPIView.as_view(), name='news-preferences'),
    path('api/news/articles/', views.NewsArticleViewSet.as_view({'get': 'list'}), name='news-articles-list'),
    path('api/news/articles/<uuid:pk>/', views.NewsArticleViewSet.as_view({'get': 'retrieve'}), name='news-articles-detail'),
    path('api/news/articles/<uuid:pk>/track_view/', views.NewsArticleViewSet.as_view({'post': 'track_view'}), name='news-articles-track-view'),
    path('api/news/articles/<uuid:pk>/track_click/', views.NewsArticleViewSet.as_view({'post': 'track_click'}), name='news-articles-track-click'),
    path('api/news/categories/', views.NewsCategoryViewSet.as_view({'get': 'list'}), name='news-categories-list'),
    
    # Debug endpoints
    path('api/debug/database/', debug_views.debug_database, name='debug-database'),
    path('api/debug/environment/', debug_env.debug_environment, name='debug-environment'),
    path('api/debug/websocket/', websocket_test.websocket_test, name='websocket-test'),
    
    # Management endpoints
    path('admin/fix-news/', management_views.fix_news_system, name='fix-news'),
    path('admin/news-status/', management_views.news_system_status, name='news-status'),
    path('api/fix-news/', management_views.api_fix_news, name='api-fix-news'),
    
    # Force fetch endpoints
    path('api/force-fetch-news/', force_fetch_views.force_fetch_marketaux_news, name='force-fetch-news'),
]
