from django.conf import settings
from django_hosts import host, patterns

from drugportals.views import get_drug


host_patterns = patterns(
    '',
    host(
        r'', settings.ROOT_URLCONF,
        name='root'),
    host(
        r'(?P<drug>[-\w]+)', 'drugportals.urls',
        callback=get_drug,
        name='portals'),
)
