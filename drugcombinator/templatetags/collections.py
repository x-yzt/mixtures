from django import template
from django.utils.translation import gettext as _


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


@register.filter
def cat(obj_1, obj_2):
    return str(obj_1) + str(obj_2)


@register.filter
def humanlist(seq):
    seq = tuple(map(str, seq))
    if len(seq) == 1:
        return seq[0]
    return ' '.join((', '.join(seq[:-1]), _("and"), seq[-1]))
