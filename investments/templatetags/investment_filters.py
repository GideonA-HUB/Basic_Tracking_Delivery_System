from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def get_price_change_class(change):
    """Get CSS class for price change styling"""
    try:
        change = float(change)
        if change > 0:
            return 'text-green-600 dark:text-green-400'
        elif change < 0:
            return 'text-red-600 dark:text-red-400'
        else:
            return 'text-gray-600 dark:text-gray-400'
    except (ValueError, TypeError):
        return 'text-gray-600 dark:text-gray-400'

@register.filter
def get_price_change_display(change):
    """Get display text for price change"""
    try:
        change = float(change)
        if change > 0:
            return f"+${change:.2f}"
        elif change < 0:
            return f"-${abs(change):.2f}"
        else:
            return "$0.00"
    except (ValueError, TypeError):
        return "$0.00"

@register.filter
def get_percentage_change_display(percentage):
    """Get display text for percentage change"""
    try:
        percentage = float(percentage)
        if percentage > 0:
            return f"+{percentage:.2f}%"
        elif percentage < 0:
            return f"{percentage:.2f}%"
        else:
            return "0.00%"
    except (ValueError, TypeError):
        return "0.00%"

@register.filter
def format_currency(amount):
    """Format amount as currency"""
    try:
        amount = float(amount)
        return f"${amount:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

@register.filter
def format_weight(weight):
    """Format weight with unit"""
    try:
        weight = float(weight)
        return f"{weight:.3f} oz"
    except (ValueError, TypeError):
        return "0.000 oz"

@register.filter
def investment_type_display(investment_type):
    """Get display text for investment type"""
    type_map = {
        'investment_only': 'Investment Only',
        'delivery_only': 'Delivery Only',
        'both': 'Investment & Delivery'
    }
    return type_map.get(investment_type, 'Unknown')
