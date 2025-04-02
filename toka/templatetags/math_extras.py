from django import template

register = template.Library()

@register.filter
def abs(value):
    # your existing abs filter
    try:
        return abs(value)
    except Exception:
        return value

@register.filter
def round(value, decimals=0):
    """
    Rounds the given value to the specified number of decimals.
    Usage in template: {{ value|round_number }} or {{ value|round_number:2 }}
    """
    try:
        return round(float(value), int(decimals))
    except (ValueError, TypeError):
        return value
