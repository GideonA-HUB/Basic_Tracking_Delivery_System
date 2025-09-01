from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Count, Sum
from django.utils import timezone
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

from .models import (
    InvestmentCategory, InvestmentItem, PriceHistory, 
    UserInvestment, InvestmentTransaction, InvestmentPortfolio
)
from .serializers import (
    InvestmentCategorySerializer, InvestmentItemSerializer, 
    InvestmentItemDetailSerializer, UserInvestmentSerializer,
    InvestmentTransactionSerializer, InvestmentPortfolioSerializer,
    CreateInvestmentTransactionSerializer, UpdateInvestmentItemSerializer,
    InvestmentChartDataSerializer, InvestmentSummarySerializer
)
from .services import nowpayments_service, price_service

logger = logging.getLogger(__name__)


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
        
        chart_data = {
            'labels': [],
            'values': [],
            'returns': []
        }
        
        for investment in investments:
            chart_data['labels'].append(investment.item.name)
            chart_data['values'].append(float(investment.current_value_usd))
            chart_data['returns'].append(float(investment.total_return_percentage))
        
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
            status_response = nowpayments_service.get_payment_status_minimal(
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
        
        context = {
            'portfolio': portfolio,
            'active_investments': active_investments,
            'recent_transactions': recent_transactions,
        }
        
        return render(request, 'investments/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error loading investment dashboard: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load investment dashboard'
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
                
                # Create a transaction for adding funds
                transaction = InvestmentTransaction.objects.create(
                    user=request.user,
                    transaction_type='purchase',
                    amount_usd=amount,
                    price_per_unit=amount,
                    payment_method=payment_method,
                    payment_status='pending',
                    description=f"Add funds to investment account - {payment_method}",
                )
                
                # If using NOWPayments (crypto), create payment
                if payment_method == 'crypto':
                    payment_response = nowpayments_service.create_payment(transaction)
                    if payment_response:
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
        transaction = get_object_or_404(InvestmentTransaction, id=transaction_id, user=request.user)
        
        if transaction.nowpayments_payment_id:
            status_response = nowpayments_service.get_payment_status_minimal(
                transaction.nowpayments_payment_id
            )
            return render(request, 'investments/payment_status.html', {
                'transaction': transaction,
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
        ).select_related('category')[:6]
        
        # Get trending items
        trending_items = InvestmentItem.objects.filter(
            is_active=True
        ).filter(
            Q(price_change_percentage_24h__gte=5) | 
            Q(price_change_percentage_24h__lte=-5)
        ).select_related('category').order_by('-price_change_percentage_24h')[:6]
        
        context = {
            'categories': categories,
            'featured_items': featured_items,
            'trending_items': trending_items,
            'items': items,
            'selected_category': selected_category,
            'search_query': search_query,
            'sort_by': sort_by,
        }
        
        return render(request, 'investments/marketplace.html', context)
        
    except Exception as e:
        logger.error(f"Error loading investment marketplace: {e}")
        return render(request, 'investments/error.html', {
            'error_message': 'Failed to load investment marketplace'
        })


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
        
        context = {
            'item': item,
            'similar_items': similar_items,
            'chart_data': chart_data,
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
        
        context = {
            'portfolio': portfolio,
            'active_investments': active_investments,
            'completed_investments': completed_investments,
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
