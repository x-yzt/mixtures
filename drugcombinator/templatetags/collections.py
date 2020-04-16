from django import template


register = template.Library()

@register.filter
def get(obj, key):
    try:
        return obj[key]
    except (KeyError, IndexError):
        return None
