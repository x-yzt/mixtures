from utils.sitemaps import FullDomainGenericSitemap
from drugportals.models import Portal


SITEMAPS = {
    'portals': FullDomainGenericSitemap(
        {
            'queryset': Portal.objects.all(),
        },
        priority = 1.0,
        changefreq = 'daily',
        protocol = 'https'
    )
}
