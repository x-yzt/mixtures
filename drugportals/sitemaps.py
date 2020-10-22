from django.contrib.sitemaps import GenericSitemap
from drugportals.models import Portal


SITEMAPS = {
    'portals': GenericSitemap(
        {
            'queryset': Portal.objects.all(),
        },
        priority = 1.0,
        changefreq = 'daily',
        protocol = 'https'
    )
}
