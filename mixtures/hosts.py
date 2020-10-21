from django.conf import settings
from django_hosts import patterns, host
from drugportals.views import _get_drug

host_patterns = patterns('',
    host(r'', settings.ROOT_URLCONF, name='root'),
    host(r'(?P<drug>[-\w]+)', 'drugportals.urls', callback=_get_drug, name='portals'),
)
