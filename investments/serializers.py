from rest_framework import serializers
from .models import (
    InvestmentCategory, InvestmentItem, PriceHistory, 
    UserInvestment, InvestmentTransaction, InvestmentPortfolio
)


class InvestmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentCategory
        fields = [
            'id', 'name', 'description', 'icon', 'color', 
            'is_active', 'created_at'
        ]


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['price', 'change_amount', 'change_percentage', 'timestamp']


class InvestmentItemSerializer(serializers.ModelSerializer):
    category = InvestmentCategorySerializer(read_only=True)
    # Removed price_history to prevent N+1 queries - only include when specifically needed
    
    class Meta:
        model = InvestmentItem
        fields = [
            'id', 'category', 'name', 'description', 'short_description',
            'current_price_usd', 'price_change_24h', 'price_change_percentage_24h',
            'weight', 'purity', 'dimensions', 'origin', 'investment_type',
            'minimum_investment', 'maximum_investment', 'total_available',
            'currently_available', 'main_image_url', 'additional_image_urls',
            'is_active', 'is_featured', 'created_at', 'updated_at'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Add computed properties
        data['is_available_for_investment'] = instance.is_available_for_investment
        data['is_available_for_delivery'] = instance.is_available_for_delivery
        
        # Add category name for JavaScript compatibility
        data['category_name'] = instance.category.name if instance.category else 'Uncategorized'
        
        # Format price change display
        if instance.price_change_24h > 0:
            data['price_change_display'] = f"+${instance.price_change_24h}"
            data['price_change_percentage_display'] = f"+{instance.price_change_percentage_24h}%"
        elif instance.price_change_24h < 0:
            data['price_change_display'] = f"-${abs(instance.price_change_24h)}"
            data['price_change_percentage_display'] = f"-{abs(instance.price_change_percentage_24h)}%"
        else:
            data['price_change_display'] = "$0.00"
            data['price_change_percentage_display'] = "0.00%"
        
        return data


class InvestmentItemDetailSerializer(InvestmentItemSerializer):
    """Detailed serializer for investment items with full information"""
    
    class Meta(InvestmentItemSerializer.Meta):
        fields = InvestmentItemSerializer.Meta.fields + [
            'price_history'
        ]


class UserInvestmentSerializer(serializers.ModelSerializer):
    item = InvestmentItemSerializer(read_only=True)
    
    class Meta:
        model = UserInvestment
        fields = [
            'id', 'item', 'investment_amount_usd', 'quantity',
            'purchase_price_per_unit', 'current_value_usd', 'total_return_usd',
            'total_return_percentage', 'investment_type', 'status',
            'purchased_at', 'updated_at', 'sold_at'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Add computed properties
        data['is_profitable'] = instance.is_profitable
        data['days_held'] = instance.days_held
        
        # Format return display
        if instance.total_return_usd > 0:
            data['total_return_display'] = f"+${instance.total_return_usd}"
            data['total_return_percentage_display'] = f"+{instance.total_return_percentage}%"
        elif instance.total_return_usd < 0:
            data['total_return_display'] = f"-${abs(instance.total_return_usd)}"
            data['total_return_percentage_display'] = f"-{abs(instance.total_return_percentage)}%"
        else:
            data['total_return_display'] = "$0.00"
            data['total_return_percentage_display'] = "0.00%"
        
        return data


class InvestmentTransactionSerializer(serializers.ModelSerializer):
    item = InvestmentItemSerializer(read_only=True)
    investment = UserInvestmentSerializer(read_only=True)
    
    class Meta:
        model = InvestmentTransaction
        fields = [
            'transaction_id', 'item', 'investment', 'transaction_type',
            'amount_usd', 'quantity', 'price_per_unit', 'payment_method',
            'payment_reference', 'payment_status', 'nowpayments_payment_id',
            'nowpayments_payment_status', 'crypto_amount', 'crypto_currency',
            'description', 'notes', 'created_at', 'updated_at', 'completed_at'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Add computed properties
        data['is_completed'] = instance.is_completed
        data['is_pending'] = instance.is_pending
        
        return data


class InvestmentPortfolioSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    
    class Meta:
        model = InvestmentPortfolio
        fields = [
            'id', 'user', 'total_invested', 'current_value', 'total_return',
            'total_return_percentage', 'active_investments_count',
            'total_investments_count', 'last_updated'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Add computed properties
        data['is_profitable'] = instance.is_profitable
        
        # Format return display
        if instance.total_return > 0:
            data['total_return_display'] = f"+${instance.total_return}"
            data['total_return_percentage_display'] = f"+{instance.total_return_percentage}%"
        elif instance.total_return < 0:
            data['total_return_display'] = f"-${abs(instance.total_return)}"
            data['total_return_percentage_display'] = f"-{abs(instance.total_return_percentage)}%"
        else:
            data['total_return_display'] = "$0.00"
            data['total_return_percentage_display'] = "0.00%"
        
        return data


class CreateInvestmentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for creating new investment transactions"""
    
    class Meta:
        model = InvestmentTransaction
        fields = [
            'item', 'transaction_type', 'amount_usd', 'investment_type',
            'description'
        ]
    
    def validate_amount_usd(self, value):
        """Validate investment amount"""
        if value <= 0:
            raise serializers.ValidationError("Investment amount must be greater than zero")
        return value
    
    def validate(self, data):
        """Validate transaction data"""
        item = data['item']
        amount = data['amount_usd']
        investment_type = data.get('investment_type', 'hold')
        
        # Check minimum investment
        if amount < item.minimum_investment:
            raise serializers.ValidationError(
                f"Minimum investment amount is ${item.minimum_investment}"
            )
        
        # Check maximum investment
        if item.maximum_investment and amount > item.maximum_investment:
            raise serializers.ValidationError(
                f"Maximum investment amount is ${item.maximum_investment}"
            )
        
        # Check if item is available for the requested type
        if investment_type == 'hold' and not item.is_available_for_investment:
            raise serializers.ValidationError(
                "This item is not available for investment"
            )
        
        if investment_type == 'delivery' and not item.is_available_for_delivery:
            raise serializers.ValidationError(
                "This item is not available for delivery"
            )
        
        return data


class UpdateInvestmentItemSerializer(serializers.ModelSerializer):
    """Serializer for updating investment item prices"""
    
    class Meta:
        model = InvestmentItem
        fields = ['current_price_usd']
    
    def validate_current_price_usd(self, value):
        """Validate new price"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value


class InvestmentChartDataSerializer(serializers.Serializer):
    """Serializer for investment chart data"""
    labels = serializers.ListField(child=serializers.CharField())
    prices = serializers.ListField(child=serializers.DecimalField(max_digits=12, decimal_places=2))
    changes = serializers.ListField(child=serializers.DecimalField(max_digits=8, decimal_places=2))


class NOWPaymentsEstimateSerializer(serializers.Serializer):
    """Serializer for NOWPayments price estimates"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    crypto_currency = serializers.CharField(max_length=10)


class InvestmentSummarySerializer(serializers.Serializer):
    """Serializer for investment summary data"""
    total_items = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    featured_items = InvestmentItemSerializer(many=True)
    recent_price_changes = PriceHistorySerializer(many=True)
