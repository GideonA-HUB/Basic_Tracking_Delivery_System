from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def div(value, arg):
    """Divide value by arg"""
    try:
        if arg == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate percentage (value / total * 100)"""
    try:
        if total == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0

@register.filter
def safe_div(value, arg, default=0):
    """Safely divide value by arg with default fallback"""
    try:
        if arg == 0 or arg is None:
            return default
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return default
