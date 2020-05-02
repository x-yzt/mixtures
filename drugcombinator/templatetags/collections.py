from django import template


register = template.Library()

@register.filter
def get(obj, key):
    try:
        return obj[key]
    except (KeyError, IndexError):
        return None


@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name, None)
