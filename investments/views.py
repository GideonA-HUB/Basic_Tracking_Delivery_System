from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Count, Sum
from django.db import connection
from django.utils import timezone

# Import news views
from .news_views import *
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from decimal import Decimal
import json
import logging
from django.contrib import messages
from django.forms import Form
from django import forms
from django.core.management import call_command
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.urls import reverse

from .models import (
    InvestmentCategory, InvestmentItem, PriceHistory, 
    UserInvestment, InvestmentTransaction, InvestmentPortfolio, RealTimePriceFeed,
    CryptoWithdrawal
)
from .serializers import (
    InvestmentCategorySerializer, InvestmentItemSerializer, 
    InvestmentItemDetailSerializer, UserInvestmentSerializer,
    InvestmentTransactionSerializer, InvestmentPortfolioSerializer,
    CreateInvestmentTransactionSerializer, UpdateInvestmentItemSerializer,
    InvestmentChartDataSerializer, InvestmentSummarySerializer,
    PriceHistorySerializer
)
from .services import nowpayments_service
from .price_services import price_service

logger = logging.getLogger(__name__)


def is_staff_user(user):
    """Check if user is staff"""
    return user.is_staff


# API Viewsets
class InvestmentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for investment categories"""
    queryset = InvestmentCategory.objects.filter(is_active=True)
    serializer_class = InvestmentCategorySerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get all items in a category"""
        category = self.get_object()
        items = InvestmentItem.objects.filter(
            category=category, 
            is_active=True
        ).order_by('-is_featured', '-created_at')
        
        serializer = InvestmentItemSerializer(items, many=True)
        return Response(serializer.data)


class InvestmentItemViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for investment items"""
    queryset = InvestmentItem.objects.filter(is_active=True)
    serializer_class = InvestmentItemSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by investment type
        investment_type = self.request.query_params.get('investment_type')
        if investment_type:
            queryset = queryset.filter(investment_type__in=[investment_type, 'both'])
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(current_price_usd__gte=min_price)
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(current_price_usd__lte=max_price)
        
        # Search by name/description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )
        
        # Sort options
        sort_by = self.request.query_params.get('sort', '-is_featured')
        if sort_by == 'price_low':
            queryset = queryset.order_by('current_price_usd')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-current_price_usd')
        elif sort_by == 'change_high':
            queryset = queryset.order_by('-price_change_percentage_24h')
        elif sort_by == 'change_low':
            queryset = queryset.order_by('price_change_percentage_24h')
        else:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InvestmentItemDetailSerializer
        return InvestmentItemSerializer
    
    @action(detail=True, methods=['get'])
    def price_history(self, request, pk=None):
        """Get price history for an item"""
        item = self.get_object()
        days = int(request.query_params.get('days', 30))
        
        chart_data = price_service.get_price_chart_data(item, days)
        serializer = InvestmentChartDataSerializer(chart_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def similar_items(self, request, pk=None):
        """Get similar investment items"""
        item = self.get_object()
        similar_items = InvestmentItem.objects.filter(
            category=item.category,
            is_active=True
        ).exclude(id=item.id)[:6]
        
        serializer = InvestmentItemSerializer(similar_items, many=True)
        return Response(serializer.data)


class UserInvestmentViewSet(viewsets.ModelViewSet):
    """ViewSet for user investments"""
    serializer_class = UserInvestmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserInvestment.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def portfolio_summary(self, request):
        """Get user's portfolio summary"""
        portfolio, created = InvestmentPortfolio.objects.get_or_create(
            user=request.user
        )
        portfolio.update_portfolio_summary()
        
        serializer = InvestmentPortfolioSerializer(portfolio)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def performance_chart(self, request):
        """Get performance chart data for user's investments"""
        investments = self.get_queryset().filter(status='active')
        
        # Generate time series data for the last 30 days
        from datetime import datetime, timedelta
        import random
        
        labels = []
        values = []
        
        # Generate sample data for the last 30 days
        from django.db import models
        base_value = float(request.user.investments.aggregate(
            total=models.Sum('investment_amount_usd')
        )['total'] or 0)
        
        current_value = base_value
        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            labels.append(date.strftime('%m/%d'))
            
            # Simulate portfolio growth with some volatility
            change_percent = random.uniform(-2, 3)  # -2% to +3% daily change
            current_value *= (1 + change_percent / 100)
            values.append(current_value)
        
        # Distribution data
        distribution_labels = []
        distribution_values = []
        
        for investment in investments:
            distribution_labels.append(investment.item.category.name)
            distribution_values.append(float(investment.current_value_usd))
        
        chart_data = {
            'labels': labels,
            'values': values,
            'distribution_labels': distribution_labels,
            'distribution_values': distribution_values
        }
        
        return Response(chart_data)


class InvestmentTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for investment transactions"""
    serializer_class = InvestmentTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return InvestmentTransaction.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateInvestmentTransactionSerializer
        return InvestmentTransactionSerializer
    
    def perform_create(self, serializer):
        """Create transaction and initiate payment"""
        transaction = serializer.save(
            user=self.request.user,
            payment_method='nowpayments',
            payment_status='pending'
        )
        
        # Set price per unit from item
        transaction.price_per_unit = transaction.item.current_price_usd
        transaction.save()
        
        # Create NOWPayments payment
        payment_response = nowpayments_service.create_payment(transaction)
        
        if payment_response:
            return Response({
                'transaction': InvestmentTransactionSerializer(transaction).data,
                'payment_url': nowpayments_service.get_payment_url(
                    payment_response['payment_id']
                ),
                'payment_id': payment_response['payment_id']
            }, status=status.HTTP_201_CREATED)
        else:
            transaction.delete()
            return Response({
                'error': 'Failed to create payment'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def payment_status(self, request, pk=None):
        """Get current payment status"""
        transaction = self.get_object()
        
        if transaction.nowpayments_payment_id:
            status_response = nowpayments_service.get_payment_status(
                transaction.nowpayments_payment_id
            )
            return Response(status_response)
        
        return Response({
            'error': 'No NOWPayments payment ID found'
        }, status=status.HTTP_400_BAD_REQUEST)


# Frontend Views
@login_required
def investment_dashboard(request):
    """Investment dashboard for authenticated users"""
    try:
        portfolio, created = InvestmentPortfolio.objects.get_or_create(
            user=request.user
        )
        portfolio.update_portfolio_summary()
        
        # Get user's active investments
        active_investments = UserInvestment.objects.filter(
            user=request.user,
            status='active'
        ).select_related('item', 'item__category')
        
        # Get recent transactions
        recent_transactions = InvestmentTransaction.objects.filter(
            user=request.user
        ).select_related('item')[:10]
        
        # Get news data for the dashboard (with better error handling)
        dashboard_news = []
        featured_news = []
        crypto_news = []
        stocks_news = []
        real_estate_news = []
        
        try:
            from .news_models import NewsArticle, NewsCategory
            # First check if news tables exist
            if NewsArticle._meta.db_table in connection.introspection.table_names():
                dashboard_news = NewsArticle.objects.filter(
                    is_active=True
                ).order_by('-published_at')[:8]
                
                featured_news = NewsArticle.objects.filter(
                    is_active=True, 
                    is_featured=True
                ).order_by('-published_at')[:4]
                
                crypto_news = NewsArticle.objects.filter(
                    is_active=True,
                    category__name__in=['crypto', 'bitcoin', 'ethereum', 'altcoins']
                ).order_by('-published_at')[:4]
                
                stocks_news = NewsArticle.objects.filter(
                    is_active=True,
                    category__name='stocks'
                ).order_by('-published_at')[:4]
                
                real_estate_news = NewsArticle.objects.filter(
                    is_active=True,
                    category__name='real_estate'
                ).order_by('-published_at')[:4]
                
                logger.info(f"Loaded {len(dashboard_news)} news articles for dashboard")
            else:
                logger.warning("News tables don't exist yet, skipping news loading")
        except Exception as e:
            logger.warning(f"Could not load news for dashboard: {e}")
            dashboard_news = []

        # Get recent withdrawals for dashboard widget
        recent_withdrawals = CryptoWithdrawal.objects.filter(
            is_public=True
        ).order_by('order_position', '-created_at')[:20]
        
        context = {
            'portfolio': portfolio,
            'active_investments': active_investments,
            'recent_transactions': recent_transactions,
            'dashboard_news': dashboard_news,
            'featured_news': featured_news,
            'crypto_news': crypto_news,
            'stocks_news': stocks_news,
            'real_estate_news': real_estate_news,
            'recent_withdrawals': recent_withdrawals,
        }
        
        return render(request, 'investments/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error loading investment dashboard: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load investment dashboard'
        })


@login_required
def enhanced_dashboard(request):
    """Enhanced real-time investment dashboard with live charts and analytics"""
    try:
        portfolio, created = InvestmentPortfolio.objects.get_or_create(
            user=request.user
        )
        portfolio.update_portfolio_summary()
        
        # Get user's active investments
        active_investments = UserInvestment.objects.filter(
            user=request.user,
            status='active'
        ).select_related('item', 'item__category')
        
        # Get recent transactions
        recent_transactions = InvestmentTransaction.objects.filter(
            user=request.user
        ).select_related('item')[:10]
        
        # Get live price data
        from .models import RealTimePriceFeed
        live_prices = RealTimePriceFeed.objects.filter(is_active=True).order_by('-last_updated')[:20]
        
        # Get price statistics
        from .models import PriceMovementStats
        from django.db import models
        today_stats = PriceMovementStats.objects.filter(
            date=timezone.now().date()
        ).aggregate(
            total_increases=models.Sum('increases_today'),
            total_decreases=models.Sum('decreases_today'),
            total_unchanged=models.Sum('unchanged_today')
        )
        
        context = {
            'portfolio': portfolio,
            'active_investments': active_investments,
            'recent_transactions': recent_transactions,
            'live_prices': live_prices,
            'price_stats': today_stats,
        }
        
        return render(request, 'investments/enhanced_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error loading enhanced dashboard: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load enhanced dashboard'
        })

@login_required
def live_dashboard(request):
    """Live real-time investment dashboard with live market data"""
    try:
        # Get featured items with real market prices
        featured_items = InvestmentItem.objects.filter(
            is_featured=True, 
            is_active=True
        ).order_by('-current_price_usd')[:12]
        
        # Get live price feeds
        from .models import RealTimePriceFeed
        live_prices = RealTimePriceFeed.objects.filter(is_active=True).order_by('-last_updated')[:20]
        
        # Get price movement statistics
        from .models import PriceMovementStats
        from django.db import models
        from django.utils import timezone
        
        today_stats = PriceMovementStats.objects.filter(
            date=timezone.now().date()
        ).aggregate(
            total_increases=models.Sum('increases_today'),
            total_decreases=models.Sum('decreases_today'),
            total_unchanged=models.Sum('unchanged_today')
        )
        
        context = {
            'featured_items': featured_items,
            'live_prices': live_prices,
            'price_stats': today_stats,
        }
        
        return render(request, 'investments/live_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error loading live dashboard: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load live dashboard'
        })


def investment_test(request):
    """Test page for investment system"""
    try:
        categories_count = InvestmentCategory.objects.filter(is_active=True).count()
        items_count = InvestmentItem.objects.filter(is_active=True).count()
        
        context = {
            'categories_count': categories_count,
            'items_count': items_count,
        }
        
        return render(request, 'investments/test.html', context)
        
    except Exception as e:
        logger.error(f"Error loading investment test: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load investment test'
        })


# Add this new view function after the existing views
class AddFundsForm(Form):
    """Form for adding funds to investment account"""
    amount = forms.DecimalField(
        min_value=Decimal('10.00'),
        max_value=Decimal('100000.00'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter amount (min $10)'
        })
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('crypto', 'Cryptocurrency (Bitcoin, Ethereum, etc.)'),
            ('bank_transfer', 'Bank Transfer'),
            ('card', 'Credit/Debit Card'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )


@login_required
def add_funds(request):
    """Add funds to user's investment account"""
    if request.method == 'POST':
        form = AddFundsForm(request.POST)
        if form.is_valid():
            try:
                amount = form.cleaned_data['amount']
                payment_method = form.cleaned_data['payment_method']
                
                # For add funds, we need to create a special transaction
                # Since InvestmentTransaction requires an item, we'll create a PaymentTransaction instead
                from .models import PaymentTransaction
                
                # Create a payment transaction for adding funds
                transaction = PaymentTransaction.objects.create(
                    payment_id=f"FUNDS_{request.user.id}_{int(timezone.now().timestamp())}",
                    payment_type='investment',
                    amount_usd=amount,
                    user=request.user,
                    payment_status='pending'
                )
                
                # If using NOWPayments (crypto), create payment
                if payment_method == 'crypto':
                    from .services import nowpayments_service
                    
                    payment_response = nowpayments_service.create_payment(
                        amount_usd=amount,
                        order_id=transaction.payment_id,
                        order_description=f"Add funds to investment account - {request.user.username}"
                    )
                    if payment_response:
                        # Update transaction with NOWPayments data
                        transaction.nowpayments_payment_id = payment_response.get('payment_id')
                        transaction.payment_address = payment_response.get('pay_address')
                        transaction.amount_crypto = payment_response.get('pay_amount')
                        transaction.crypto_currency = payment_response.get('pay_currency')
                        transaction.save()
                        
                        messages.success(request, f'Payment initiated for ${amount}. Please complete the payment.')
                        return redirect('investments:payment-status', transaction_id=transaction.id)
                    else:
                        messages.error(request, 'Failed to create payment. Please try again.')
                        transaction.delete()
                else:
                    # For other payment methods, mark as processing
                    transaction.payment_status = 'processing'
                    transaction.save()
                    messages.success(request, f'Fund request submitted for ${amount}. We will process your payment.')
                    return redirect('investments:user-portfolio')
                    
            except Exception as e:
                logger.error(f"Error adding funds: {e}")
                messages.error(request, 'An error occurred. Please try again.')
    else:
        form = AddFundsForm()
    
    return render(request, 'investments/add_funds.html', {'form': form})


@login_required
def payment_status(request, transaction_id):
    """Check payment status for a transaction"""
    try:
        # Try to find the transaction in both models
        from .models import PaymentTransaction, InvestmentTransaction
        
        # First try PaymentTransaction (for add funds, membership)
        try:
            transaction = PaymentTransaction.objects.get(id=transaction_id, user=request.user)
            transaction_type = 'payment'
        except PaymentTransaction.DoesNotExist:
            # Then try InvestmentTransaction
            try:
                transaction = InvestmentTransaction.objects.get(id=transaction_id, user=request.user)
                transaction_type = 'investment'
            except InvestmentTransaction.DoesNotExist:
                messages.error(request, 'Transaction not found.')
                return redirect('investments:user-portfolio')
        
        if transaction.nowpayments_payment_id:
            status_response = nowpayments_service.get_payment_status(
                transaction.nowpayments_payment_id
            )
            return render(request, 'investments/payment_status.html', {
                'transaction': transaction,
                'transaction_type': transaction_type,
                'payment_status': status_response
            })
        else:
            messages.error(request, 'No payment information found.')
            return redirect('investments:user-portfolio')
            
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
        messages.error(request, 'Failed to check payment status.')
        return redirect('investments:user-portfolio')


# Update the marketplace view to handle category filtering better
def investment_marketplace(request):
    """Public marketplace for browsing investment items"""
    try:
        # Get categories
        categories = InvestmentCategory.objects.filter(is_active=True)
        
        # Get selected category
        selected_category = request.GET.get('category')
        search_query = request.GET.get('search', '')
        sort_by = request.GET.get('sort', '-is_featured')
        
        # Base queryset
        items = InvestmentItem.objects.filter(is_active=True).select_related('category')
        
        # Apply filters
        if selected_category:
            items = items.filter(category_id=selected_category)
        
        if search_query:
            items = items.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Apply sorting
        if sort_by == 'price_low':
            items = items.order_by('current_price_usd')
        elif sort_by == 'price_high':
            items = items.order_by('-current_price_usd')
        elif sort_by == 'change_high':
            items = items.order_by('-price_change_percentage_24h')
        elif sort_by == 'newest':
            items = items.order_by('-created_at')
        else:
            items = items.order_by('-is_featured', '-created_at')
        
        # Get featured items (for display at top)
        featured_items = InvestmentItem.objects.filter(
            is_active=True,
            is_featured=True
        ).select_related('category').order_by('-created_at')[:6]
        
        # Debug logging for featured items (remove in production)
        if featured_items.count() == 0:
            logger.warning("No featured items found - this may indicate a problem")
        else:
            logger.info(f"Found {featured_items.count()} featured items for marketplace")
        
        # Get trending items
        trending_items = InvestmentItem.objects.filter(
            is_active=True
        ).filter(
            Q(price_change_percentage_24h__gte=5) | 
            Q(price_change_percentage_24h__lte=-5)
        ).select_related('category').order_by('-price_change_percentage_24h')[:6]
        
        # Debug logging removed
        
        # Get news data for the marketplace
        try:
            from .news_models import NewsArticle
            marketplace_news = NewsArticle.objects.filter(
                is_active=True,
                category__name__in=['crypto', 'stocks', 'real_estate', 'general']
            ).order_by('-published_at')[:6]
        except Exception as e:
            logger.warning(f"Could not load news for marketplace: {e}")
            marketplace_news = []

        context = {
            'categories': categories,
            'featured_items': featured_items,
            'trending_items': trending_items,
            'items': items,
            'selected_category': selected_category,
            'search_query': search_query,
            'sort_by': sort_by,
            'marketplace_news': marketplace_news,
        }
        
        return render(request, 'investments/marketplace.html', context)
        
    except Exception as e:
        logger.error(f"Error loading investment marketplace: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load investment marketplace'
        })


def test_marketplace_debug(request):
    """Debug view to test marketplace data"""
    try:
        # Get all active items
        items = InvestmentItem.objects.filter(is_active=True).select_related('category')
        
        # Get featured items
        featured_items = InvestmentItem.objects.filter(
            is_active=True,
            is_featured=True
        ).select_related('category')[:6]
        
        # Get non-featured items
        non_featured_items = InvestmentItem.objects.filter(
            is_active=True,
            is_featured=False
        ).select_related('category')
        
        context = {
            'total_items': items.count(),
            'featured_items_count': featured_items.count(),
            'non_featured_items_count': non_featured_items.count(),
            'items': items,
            'featured_items': featured_items,
            'non_featured_items': non_featured_items,
        }
        
        return render(request, 'investments/test_marketplace_debug.html', context)
        
    except Exception as e:
        return HttpResponse(f"Error: {e}")


def investment_item_detail(request, item_id):
    """Detail view for investment items"""
    try:
        item = get_object_or_404(InvestmentItem, id=item_id, is_active=True)
        
        # Get similar items
        similar_items = InvestmentItem.objects.filter(
            category=item.category,
            is_active=True
        ).exclude(id=item.id)[:4]
        
        # Get price history for chart
        chart_data = price_service.get_price_chart_data(item, days=30)
        
        # Get related news based on item category
        related_news = []
        try:
            from .news_models import NewsArticle
            if NewsArticle._meta.db_table in connection.introspection.table_names():
                # Determine news category based on item category
                if item.category.name == 'Cryptocurrency':
                    related_news = NewsArticle.objects.filter(
                        is_active=True,
                        category__name__in=['crypto', 'bitcoin', 'ethereum', 'altcoins']
                    ).order_by('-published_at')[:6]
                elif item.category.name == 'Real Estate':
                    related_news = NewsArticle.objects.filter(
                        is_active=True,
                        category__name='real_estate'
                    ).order_by('-published_at')[:6]
                elif item.category.name == 'Stocks':
                    related_news = NewsArticle.objects.filter(
                        is_active=True,
                        category__name='stocks'
                    ).order_by('-published_at')[:6]
                else:
                    # General news for other categories
                    related_news = NewsArticle.objects.filter(
                        is_active=True
                    ).order_by('-published_at')[:6]
                
                logger.info(f"Loaded {len(related_news)} related news articles for item {item.name}")
        except Exception as e:
            logger.warning(f"Could not load related news for item {item.name}: {e}")
            related_news = []
        
        context = {
            'item': item,
            'similar_items': similar_items,
            'chart_data': chart_data,
            'related_news': related_news,
        }
        
        return render(request, 'investments/item_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error loading investment item detail: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load investment item details'
        })


@login_required
def user_portfolio(request):
    """User's investment portfolio page"""
    try:
        portfolio, created = InvestmentPortfolio.objects.get_or_create(
            user=request.user
        )
        portfolio.update_portfolio_summary()
        
        # Get all user investments
        investments = UserInvestment.objects.filter(
            user=request.user
        ).select_related('item', 'item__category').order_by('-purchased_at')
        
        # Group by status
        active_investments = investments.filter(status='active')
        completed_investments = investments.filter(status__in=['sold', 'delivered'])
        
        # Get news data for the portfolio
        try:
            from .news_models import NewsArticle
            portfolio_news = NewsArticle.objects.filter(
                is_active=True,
                category__name__in=['crypto', 'stocks', 'real_estate', 'general']
            ).order_by('-published_at')[:8]
        except Exception as e:
            logger.warning(f"Could not load news for portfolio: {e}")
            portfolio_news = []

        context = {
            'portfolio': portfolio,
            'active_investments': active_investments,
            'completed_investments': completed_investments,
            'portfolio_news': portfolio_news,
        }
        
        return render(request, 'investments/portfolio.html', context)
        
    except Exception as e:
        logger.error(f"Error loading user portfolio: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load portfolio'
        })


# NOWPayments Webhook Handler
@csrf_exempt
@require_http_methods(["POST"])
def nowpayments_webhook(request):
    """Handle NOWPayments webhook notifications"""
    try:
        # Get signature from headers
        signature = request.headers.get('x-nowpayments-sig')
        if not signature:
            logger.error("No signature found in webhook")
            return HttpResponse(status=400)
        
        # Process webhook
        success = nowpayments_service.process_webhook(
            request.body.decode('utf-8'),
            signature
        )
        
        if success:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
            
    except Exception as e:
        logger.error(f"Error processing NOWPayments webhook: {e}")
        return HttpResponse(status=500)


# Admin Views
@login_required
def admin_investment_management(request):
    """Admin interface for managing investments"""
    if not request.user.is_staff:
        return HttpResponse(status=403)
    
    try:
        # Get investment summary
        total_items = InvestmentItem.objects.filter(is_active=True).count()
        total_categories = InvestmentCategory.objects.filter(is_active=True).count()
        total_users = UserInvestment.objects.values('user').distinct().count()
        total_investments = UserInvestment.objects.filter(status='active').count()
        
        # Get recent price changes
        recent_price_changes = PriceHistory.objects.select_related('item').order_by('-timestamp')[:10]
        
        # Get investment statistics
        investment_stats = UserInvestment.objects.filter(
            status='active'
        ).aggregate(
            total_invested=Sum('investment_amount_usd'),
            total_current_value=Sum('current_value_usd'),
            total_return=Sum('total_return_usd')
        )
        
        context = {
            'total_items': total_items,
            'total_categories': total_categories,
            'total_users': total_users,
            'total_investments': total_investments,
            'recent_price_changes': recent_price_changes,
            'investment_stats': investment_stats,
        }
        
        return render(request, 'investments/admin_management.html', context)
        
    except Exception as e:
        logger.error(f"Error loading admin investment management: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load admin management'
        })


@login_required
def admin_manage_categories(request):
    """Custom view for managing investment categories"""
    if not request.user.is_staff:
        return HttpResponse(status=403)
    
    try:
        categories = InvestmentCategory.objects.all().order_by('name')
        context = {
            'categories': categories,
        }
        return render(request, 'investments/admin_categories.html', context)
    except Exception as e:
        logger.error(f"Error loading categories management: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load categories management'
        })


@login_required
def admin_manage_items(request):
    """Custom view for managing investment items"""
    if not request.user.is_staff:
        return HttpResponse(status=403)
    
    try:
        items = InvestmentItem.objects.all().select_related('category').order_by('name')
        context = {
            'items': items,
        }
        return render(request, 'investments/admin_items.html', context)
    except Exception as e:
        logger.error(f"Error loading items management: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load items management'
        })


@login_required
def admin_add_category(request):
    """Custom view for adding investment categories"""
    if not request.user.is_staff:
        return HttpResponse(status=403)
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            is_active = request.POST.get('is_active') == 'on'
            
            if name:
                category = InvestmentCategory.objects.create(
                    name=name,
                    description=description,
                    is_active=is_active
                )
                messages.success(request, f'Category "{name}" created successfully!')
                return redirect('investments:admin-manage-categories')
            else:
                messages.error(request, 'Category name is required.')
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            messages.error(request, 'Failed to create category.')
    
    return render(request, 'investments/admin_add_category.html')


@login_required
def admin_add_item(request):
    """Custom view for adding investment items"""
    if not request.user.is_staff:
        return HttpResponse(status=403)
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            category_id = request.POST.get('category')
            description = request.POST.get('description', '')
            price = request.POST.get('price')
            minimum_investment = request.POST.get('minimum_investment', price)
            investment_type = request.POST.get('investment_type')
            is_active = request.POST.get('is_active') == 'on'
            is_featured = request.POST.get('is_featured') == 'on'
            
            if name and category_id and price:
                category = InvestmentCategory.objects.get(id=category_id)
                item = InvestmentItem.objects.create(
                    name=name,
                    category=category,
                    description=description,
                    short_description=description[:300] if description else '',
                    current_price_usd=price,
                    minimum_investment=minimum_investment,
                    investment_type=investment_type or 'both',
                    is_active=is_active,
                    is_featured=is_featured
                )
                messages.success(request, f'Investment item "{name}" created successfully!')
                return redirect('investments:admin-manage-items')
            else:
                messages.error(request, 'Name, category, and price are required.')
        except Exception as e:
            logger.error(f"Error creating investment item: {e}")
            messages.error(request, 'Failed to create investment item.')
    
    categories = InvestmentCategory.objects.filter(is_active=True)
    context = {
        'categories': categories,
        'investment_types': InvestmentItem.INVESTMENT_TYPE_CHOICES,
    }
    return render(request, 'investments/admin_add_item.html')


# API Summary Endpoint
class InvestmentSummaryView(View):
    """Get investment system summary"""
    
    def get(self, request):
        try:
            # Get summary data
            total_items = InvestmentItem.objects.filter(is_active=True).count()
            total_categories = InvestmentCategory.objects.filter(is_active=True).count()
            featured_items = InvestmentItem.objects.filter(
                is_active=True,
                is_featured=True
            ).select_related('category')[:6]
            
            recent_price_changes = PriceHistory.objects.select_related('item').order_by('-timestamp')[:10]
            
            summary_data = {
                'total_items': total_items,
                'total_categories': total_categories,
                'featured_items': InvestmentItemSerializer(featured_items, many=True).data,
                'recent_price_changes': PriceHistorySerializer(recent_price_changes, many=True).data,
            }
            
            serializer = InvestmentSummarySerializer(summary_data)
            return JsonResponse(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting investment summary: {e}")
            return JsonResponse({
                'error': 'Failed to get investment summary'
            }, status=500)


# New API endpoints for dashboard
class PriceStatisticsView(View):
    """Get price movement statistics"""
    
    def get(self, request):
        try:
            from .models import PriceMovementStats
            
            # Get today's statistics
            from django.db import models
            today_stats = PriceMovementStats.objects.filter(
                date=timezone.now().date()
            ).aggregate(
                total_increases=models.Sum('increases_today'),
                total_decreases=models.Sum('decreases_today'),
                total_unchanged=models.Sum('unchanged_today')
            )
            
            total_increases = today_stats['total_increases'] or 0
            total_decreases = today_stats['total_decreases'] or 0
            total_unchanged = today_stats['total_unchanged'] or 0
            total_movements = total_increases + total_decreases + total_unchanged
            
            data = {
                'increases': total_increases,
                'decreases': total_decreases,
                'unchanged': total_unchanged,
                'total': total_movements,
                'timestamp': timezone.now().isoformat()
            }
            
            return JsonResponse(data)
            
        except Exception as e:
            logger.error(f"Error getting price statistics: {e}")
            return JsonResponse({
                'error': 'Failed to get price statistics'
            }, status=500)


class LivePricesView(View):
    """Get live prices for all active items"""
    
    def get(self, request):
        try:
            from .models import RealTimePriceFeed
            
            # Get all active price feeds
            feeds = RealTimePriceFeed.objects.filter(is_active=True)
            prices = []
            
            for feed in feeds:
                prices.append({
                    'symbol': feed.symbol,
                    'name': feed.name,
                    'current_price': float(feed.current_price),
                    'price_change_24h': float(feed.price_change_24h),
                    'price_change_percentage_24h': float(feed.price_change_percentage_24h),
                    'last_updated': feed.last_updated.isoformat() if feed.last_updated else None,
                    'source': 'price_feed'
                })
            
            # Also include investment items that don't have price feeds
            items = InvestmentItem.objects.filter(is_active=True)
            for item in items:
                # Check if we already have this item from price feeds
                if not any(p['name'] == item.name for p in prices):
                    prices.append({
                        'symbol': item.symbol,
                        'name': item.name,
                        'current_price': float(item.current_price_usd),
                        'price_change_24h': float(item.price_change_24h),
                        'price_change_percentage_24h': float(item.price_change_percentage_24h),
                        'last_updated': item.last_price_update.isoformat() if item.last_price_update else None,
                        'source': 'investment_item'
                    })
            
            data = {
                'prices': prices,
                'total_items': len(prices),
                'timestamp': timezone.now().isoformat()
            }
            
            return JsonResponse(data)
            
        except Exception as e:
            logger.error(f"Error getting live prices: {e}")
            return JsonResponse({
                'error': 'Failed to get live prices'
            }, status=500)


# Add this new view after the existing views
@login_required
def invest_in_item(request, item_id, investment_type):
    """Handle investment in a specific item"""
    try:
        item = get_object_or_404(InvestmentItem, id=item_id, is_active=True)
        
        if request.method == 'POST':
            amount = request.POST.get('amount')
            quantity = request.POST.get('quantity')
            
            if not amount or not quantity:
                messages.error(request, 'Please provide investment amount and quantity.')
                return redirect('investments:investment-item-detail', item_id=item_id)
            
            try:
                amount = Decimal(amount)
                quantity = Decimal(quantity)
            except (ValueError, TypeError):
                messages.error(request, 'Invalid amount or quantity.')
                return redirect('investments:investment-item-detail', item_id=item_id)
            
            # Validate minimum investment
            if amount < item.minimum_investment:
                messages.error(request, f'Minimum investment amount is ${item.minimum_investment}.')
                return redirect('investments:investment-item-detail', item_id=item_id)
            
            # Get payment method from form
            payment_method = request.POST.get('payment_method', 'crypto')
            
            # Create investment transaction
            transaction = InvestmentTransaction.objects.create(
                user=request.user,
                item=item,
                transaction_type='purchase',
                amount_usd=amount,
                quantity=quantity,
                price_per_unit=item.current_price_usd,
                payment_method=payment_method,
                payment_status='pending',
                description=f"{investment_type.title()} of {item.name}",
            )
            
            # Handle different payment methods
            if payment_method == 'crypto':
                # Check if NOWPayments service is properly configured
                if not nowpayments_service.api_key or not nowpayments_service.api_key.strip():
                    messages.error(request, '❌ NOWPayments API key not configured. Please contact support.')
                    transaction.delete()
                    return redirect('investments:investment-item-detail', item_id=item_id)
                
                if not nowpayments_service.ipn_callback_url:
                    messages.error(request, '❌ NOWPayments IPN callback URL not configured. This is required for payment processing.')
                    messages.error(request, '🔧 Please add NOWPAYMENTS_IPN_URL to your Railway environment variables.')
                    messages.error(request, '📋 Required value: https://meridian-asset-logistics.up.railway.app/investments/api/payments/ipn/')
                    transaction.delete()
                    return redirect('investments:investment-item-detail', item_id=item_id)
                
                # Create NOWPayments payment for cryptocurrency
                logger.info(f"Creating investment payment for user {request.user.username}, amount: ${amount}, item: {item.name}")
                
                payment_response = nowpayments_service.create_investment_payment(
                    user=request.user,
                    amount_usd=amount,
                    investment_type=investment_type,
                    item=item,
                    transaction=transaction
                )
                
                logger.info(f"Investment payment response: {payment_response}")
                
                if payment_response and payment_response.get('success'):
                    # Update transaction with NOWPayments data
                    transaction.nowpayments_payment_id = payment_response.get('nowpayments_payment_id')
                    transaction.save()
                    
                    logger.info(f"Investment payment created successfully, redirecting to payment details")
                    # Redirect to payment details page
                    return redirect('investments:investment-payment-details', transaction_id=transaction.id)
                else:
                    error_msg = payment_response.get('error', 'Unknown error') if payment_response else 'No response from payment service'
                    logger.error(f"Failed to create investment payment: {error_msg}")
                    messages.error(request, f'Failed to create cryptocurrency payment: {error_msg}')
                    transaction.delete()
                    return redirect('investments:investment-item-detail', item_id=item_id)
            else:
                # Handle bank transfer (you can implement this later)
                messages.info(request, 'Bank transfer option will be available soon.')
                transaction.delete()
                return redirect('investments:investment-item-detail', item_id=item_id)
        
        # GET request - show investment form
        context = {
            'item': item,
            'investment_type': investment_type,
            'type_display': 'Investment' if investment_type == 'hold' else 'Buy & Deliver'
        }
        
        return render(request, 'investments/invest_in_item.html', context)
        
    except Exception as e:
        logger.error(f"Error in invest_in_item: {e}")
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('investments:investment-marketplace')


@login_required
def investment_success(request, transaction_id):
    """Handle successful investment completion"""
    try:
        transaction = get_object_or_404(InvestmentTransaction, id=transaction_id, user=request.user)
        
        # Create user investment if payment is completed
        if transaction.payment_status == 'completed':
            investment = UserInvestment.objects.create(
                user=request.user,
                item=transaction.item,
                investment_amount_usd=transaction.amount_usd,
                quantity=transaction.quantity,
                purchase_price_per_unit=transaction.price_per_unit,
                investment_type=transaction.description.split()[0].lower(),  # Extract type from description
                status='active'
            )
            
            # Update current value
            investment.current_value_usd = investment.quantity * investment.item.current_price_usd
            investment.total_return_usd = investment.current_value_usd - investment.investment_amount_usd
            if investment.investment_amount_usd > 0:
                investment.total_return_percentage = (investment.total_return_usd / investment.investment_amount_usd) * 100
            investment.save()
            
            # Update portfolio
            portfolio, created = InvestmentPortfolio.objects.get_or_create(user=request.user)
            portfolio.update_portfolio_summary()
            
            messages.success(request, f'Investment in {transaction.item.name} completed successfully!')
            return redirect('investments:user-portfolio')
        else:
            messages.warning(request, 'Payment is still processing. Please wait for confirmation.')
            return redirect('investments:user-portfolio')
            
    except Exception as e:
        logger.error(f"Error in investment_success: {e}")
        messages.error(request, 'An error occurred. Please contact support.')
        return redirect('investments:investment-marketplace')


@login_required
def investment_cancel(request, transaction_id):
    """Handle cancelled investment"""
    try:
        transaction = get_object_or_404(InvestmentTransaction, id=transaction_id, user=request.user)
        
        if transaction.payment_status == 'pending':
            transaction.payment_status = 'cancelled'
            transaction.save()
            messages.info(request, 'Investment was cancelled.')
        
        return redirect('investments:investment-marketplace')
        
    except Exception as e:
        logger.error(f"Error in investment_cancel: {e}")
        messages.error(request, 'An error occurred.')
        return redirect('investments:investment-marketplace')


@user_passes_test(is_staff_user)
def fix_production_database_view(request):
    """View to fix production database issues"""
    if request.method == 'POST':
        try:
            # Call the management command
            call_command('fix_production_db', verbosity=0)
            messages.success(request, '✅ Production database fixed successfully! Live price updates should now work.')
            
            # Redirect to admin or show success
            return redirect('admin:investments_real_time_price_feed_changelist')
            
        except Exception as e:
            messages.error(request, f'❌ Error fixing production database: {str(e)}')
            logger.error(f"Error fixing production database: {e}")
    
    # Show the fix form
    context = {
        'title': 'Fix Production Database',
        'description': 'This will fix missing last_price_update fields and create price feeds for live updates.'
    }
    return render(request, 'investments/fix_production_db.html', context)

# NOWPayments Webhook and Payment Views
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def nowpayments_ipn_webhook(request):
    """Handle NOWPayments IPN (Instant Payment Notification) webhooks"""
    try:
        # Get the raw request body
        body = request.body.decode('utf-8')
        
        # Get the signature header
        signature = request.headers.get('X-NowPayments-Sig')
        
        if not signature:
            logger.error("Missing NOWPayments signature header")
            return HttpResponse(status=400)
        
        # Verify the signature
        from .services import nowpayments_service
        if not nowpayments_service.verify_ipn_signature(body, signature):
            logger.error("Invalid NOWPayments IPN signature")
            return HttpResponse(status=400)
        
        # Parse the JSON data
        try:
            ipn_data = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in IPN: {e}")
            return HttpResponse(status=400)
        
        # Process the IPN data
        if nowpayments_service.process_ipn_data(ipn_data):
            logger.info(f"IPN processed successfully for payment {ipn_data.get('payment_id')}")
            return HttpResponse(status=200)
        else:
            logger.error(f"Failed to process IPN for payment {ipn_data.get('payment_id')}")
            return HttpResponse(status=500)
            
    except Exception as e:
        logger.error(f"Error processing NOWPayments IPN: {str(e)}")
        return HttpResponse(status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_membership_payment(request):
    """Create a new membership payment request"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Get amount from request (default to $1,270)
        data = json.loads(request.body) if request.body else {}
        amount = data.get('amount', 1270.00)
        
        # Create membership payment
        from .services import nowpayments_service
        
        # Check if NOWPayments service is properly configured
        if not nowpayments_service.api_key or not nowpayments_service.api_key.strip():
            logger.error("NOWPayments API key not configured")
            return JsonResponse({'error': 'Payment service not configured. Please contact support.'}, status=500)
        
        transaction = nowpayments_service.create_membership_payment(request.user, amount)
        
        if transaction:
            # Return payment details
            response_data = {
                'success': True,
                'payment_id': transaction.payment_id,
                'amount_usd': float(transaction.amount_usd),
                'crypto_amount': float(transaction.amount_crypto) if transaction.amount_crypto else None,
                'crypto_currency': transaction.crypto_currency,
                'payment_address': transaction.payment_address,
                'payment_status': transaction.payment_status,
                'payment_url': f"https://nowpayments.io/payment/?iid={transaction.nowpayments_payment_id}"
            }
            return JsonResponse(response_data)
        else:
            logger.error("NOWPayments service returned None for membership payment")
            return JsonResponse({'error': 'Failed to create payment. Please try again or contact support.'}, status=500)
            
    except Exception as e:
        logger.error(f"Error creating membership payment: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["GET"])
def get_payment_status(request, payment_id):
    """Get payment status for a specific payment"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Get payment transaction
        from .models import PaymentTransaction
        try:
            transaction = PaymentTransaction.objects.get(
                payment_id=payment_id,
                user=request.user
            )
        except PaymentTransaction.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)
        
        # Return payment details
        response_data = {
            'payment_id': transaction.payment_id,
            'payment_type': transaction.payment_type,
            'amount_usd': float(transaction.amount_usd),
            'crypto_amount': float(transaction.amount_crypto) if transaction.amount_crypto else None,
            'crypto_currency': transaction.crypto_currency,
            'payment_status': transaction.payment_status,
            'payment_address': transaction.payment_address,
            'created_at': transaction.created_at.isoformat(),
            'paid_at': transaction.paid_at.isoformat() if transaction.paid_at else None,
            'is_paid': transaction.is_paid,
            'is_failed': transaction.is_failed,
            'is_pending': transaction.is_pending
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["GET"])
def user_payments_list(request):
    """Get list of user's payment transactions"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Get user's payments
        from .models import PaymentTransaction
        payments = PaymentTransaction.objects.filter(user=request.user).order_by('-created_at')
        
        payments_data = []
        for payment in payments:
            payments_data.append({
                'payment_id': payment.payment_id,
                'payment_type': payment.payment_type,
                'amount_usd': float(payment.amount_usd),
                'crypto_amount': float(payment.amount_crypto) if payment.amount_crypto else None,
                'crypto_currency': payment.crypto_currency,
                'payment_status': payment.payment_status,
                'created_at': payment.created_at.isoformat(),
                'paid_at': payment.paid_at.isoformat() if payment.paid_at else None,
                'is_paid': payment.is_paid,
                'is_failed': payment.is_failed,
                'is_pending': payment.is_pending
            })
        
        return JsonResponse({
            'success': True,
            'payments': payments_data,
            'total_count': len(payments_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting user payments: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@require_http_methods(["GET"])
def check_membership_status(request):
    """Check if user has active membership"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Check for active membership
        from .models import MembershipPayment
        try:
            membership = MembershipPayment.objects.get(
                user=request.user,
                is_active=True
            )
            
            response_data = {
                'has_membership': True,
                'membership_type': membership.membership_type,
                'membership_duration': membership.membership_duration,
                'activated_at': membership.activated_at.isoformat(),
                'expires_at': membership.expires_at.isoformat(),
                'days_remaining': membership.days_remaining,
                'is_active': membership.is_active
            }
        except MembershipPayment.DoesNotExist:
            response_data = {
                'has_membership': False,
                'membership_type': None,
                'membership_duration': None,
                'activated_at': None,
                'expires_at': None,
                'days_remaining': 0,
                'is_active': False
            }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error checking membership status: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required
def investment_payment_details(request, transaction_id):
    """Show investment payment details and instructions"""
    try:
        transaction = get_object_or_404(InvestmentTransaction, id=transaction_id, user=request.user)
        
        if not transaction.nowpayments_payment_id:
            messages.error(request, 'Payment not found or invalid.')
            return redirect('investments:investment-marketplace')
        
        context = {
            'transaction': transaction,
            'item': transaction.item,
            'user': request.user
        }
        return render(request, 'investments/investment_payment_details.html', context)
        
    except Exception as e:
        logger.error(f"Error in investment_payment_details: {str(e)}")
        messages.error(request, 'An error occurred. Please try again.')
        return redirect('investments:investment-marketplace')

@login_required
def check_investment_payment_status(request, transaction_id):
    """Check payment status for a specific investment transaction"""
    try:
        transaction = get_object_or_404(InvestmentTransaction, id=transaction_id, user=request.user)
        
        # Return payment details
        response_data = {
            'transaction_id': transaction.id,
            'payment_status': transaction.payment_status,
            'nowpayments_status': transaction.nowpayments_payment_status,
            'amount_usd': float(transaction.amount_usd),
            'crypto_amount': float(transaction.crypto_amount) if transaction.crypto_amount else None,
            'crypto_currency': transaction.crypto_currency,
            'payment_address': transaction.payment_address,
            'created_at': transaction.created_at.isoformat(),
            'completed_at': transaction.completed_at.isoformat() if transaction.completed_at else None,
            'is_completed': transaction.payment_status == 'completed',
            'is_failed': transaction.payment_status == 'failed',
            'is_pending': transaction.payment_status == 'pending'
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error checking investment payment status: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def membership_payment_view(request):
    """View for membership payment page"""
    if not request.user.is_authenticated:
        return redirect('accounts:customer_login')
    
    context = {
        'user': request.user,
    }
    return render(request, 'investments/membership_payment.html', context)


@login_required
def nowpayments_config_status(request):
    """Debug view to show NOWPayments configuration status"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff only.')
        return redirect('investments:investment-marketplace')
    
    config_status = {
        'api_key': '✅ Configured' if nowpayments_service.api_key and nowpayments_service.api_key.strip() else '❌ Missing',
        'api_key_preview': nowpayments_service.api_key[:10] + '...' if nowpayments_service.api_key else 'None',
        'ipn_secret': '✅ Configured' if nowpayments_service.ipn_secret else '❌ Missing',
        'ipn_callback_url': '✅ Configured' if nowpayments_service.ipn_callback_url else '❌ Missing',
        'ipn_url_value': nowpayments_service.ipn_callback_url or 'Not set',
        'api_url': nowpayments_service.api_url,
    }
    
    context = {
        'config_status': config_status,
        'required_vars': [
            'NOWPAYMENTS_API_KEY',
            'NOWPAYMENTS_IPN_SECRET', 
            'NOWPAYMENTS_IPN_URL',
            'NOWPAYMENTS_API_URL'
        ]
    }
    
    return render(request, 'investments/nowpayments_config_status.html', context)


def meridian_quick_access(request):
    """Meridian Quick Access page for expert trading insights and management"""
    context = {
        'title': 'Meridian Quick Access',
        'description': 'Get expert trading insights and professional investment management',
        'crypto_address': 'GkJr9Rrzc3eiuetdpAJonkkeBtRAf1UvcndbQJAF7PJk'
    }
    return render(request, 'investments/meridian_quick_access.html', context)


def withdrawal_list(request):
    """Display ALL crypto withdrawals"""
    # Get ALL public withdrawals
    withdrawals = CryptoWithdrawal.objects.filter(
        is_public=True
    ).order_by('order_position', '-created_at')
    
    # Get total count
    total_count = withdrawals.count()
    
    context = {
        'withdrawals': withdrawals,
        'total_count': total_count,
        'show_more': False,  # No need for "View More" since we show all
        'title': 'Crypto Withdrawal List'
    }
    
    return render(request, 'investments/withdrawal_list.html', context)


def withdrawal_list_all(request):
    """Display all crypto withdrawals"""
    withdrawals = CryptoWithdrawal.objects.filter(
        is_public=True
    ).order_by('order_position', '-created_at')
    
    # Show all withdrawals without pagination
    context = {
        'withdrawals': withdrawals,
        'title': 'All Crypto Withdrawals'
    }
    
    return render(request, 'investments/withdrawal_list_all.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def create_fast_track_payment(request):
    """Create a fast track payment for withdrawal priority"""
    try:
        data = json.loads(request.body)
        customer_name = data.get('customer_name', '').strip()
        amount = data.get('amount', 700)  # Default $700 for fast track
        
        if not customer_name:
            return JsonResponse({
                'success': False,
                'error': 'Customer name is required'
            })
        
        # Create withdrawal entry
        withdrawal = CryptoWithdrawal.objects.create(
            name=customer_name,
            amount=Decimal(str(amount)),
            currency='USD',
            crypto_currency='BTC',
            status='pending',
            priority='fast',
            is_public=True,
            notes='Fast track payment - awaiting crypto payment'
        )
        
        # Generate payment address using NOWPayments
        try:
            payment_data = nowpayments_service.create_payment(
                price_amount=float(amount),
                price_currency='usd',
                pay_currency='btc',
                order_id=f"fast_track_{withdrawal.id}",
                order_description=f"Fast track withdrawal for {customer_name}"
            )
            
            if payment_data and 'payment_address' in payment_data:
                withdrawal.payment_id = payment_data.get('payment_id', '')
                withdrawal.payment_address = payment_data['payment_address']
                withdrawal.payment_amount = Decimal(str(payment_data.get('pay_amount', 0)))
                withdrawal.save()
                
                return JsonResponse({
                    'success': True,
                    'withdrawal_id': withdrawal.id,
                    'payment_address': withdrawal.payment_address,
                    'payment_amount': str(withdrawal.payment_amount),
                    'crypto_currency': withdrawal.crypto_currency,
                    'message': 'Payment address generated successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to generate payment address'
                })
                
        except Exception as e:
            logger.error(f"NOWPayments error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Payment service temporarily unavailable'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        logger.error(f"Fast track payment error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your request'
        })


@csrf_exempt
@require_http_methods(["POST"])
def check_payment_status(request):
    """Check payment status for a withdrawal"""
    try:
        data = json.loads(request.body)
        withdrawal_id = data.get('withdrawal_id')
        
        if not withdrawal_id:
            return JsonResponse({
                'success': False,
                'error': 'Withdrawal ID is required'
            })
        
        withdrawal = get_object_or_404(CryptoWithdrawal, id=withdrawal_id)
        
        # Check payment status with NOWPayments
        if withdrawal.payment_id:
            try:
                payment_status = nowpayments_service.get_payment_status(withdrawal.payment_id)
                
                if payment_status and payment_status.get('payment_status') == 'finished':
                    withdrawal.status = 'processing'
                    withdrawal.processed_at = timezone.now()
                    withdrawal.save()
                    
                    return JsonResponse({
                        'success': True,
                        'status': 'paid',
                        'message': 'Payment confirmed! Your withdrawal is now being processed.'
                    })
                else:
                    return JsonResponse({
                        'success': True,
                        'status': 'pending',
                        'message': 'Payment is still pending. Please complete the payment.'
                    })
                    
            except Exception as e:
                logger.error(f"Payment status check error: {str(e)}")
                return JsonResponse({
                    'success': True,
                    'status': 'unknown',
                    'message': 'Unable to verify payment status. Please contact support.'
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No payment ID found for this withdrawal'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        logger.error(f"Payment status check error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while checking payment status'
        })
