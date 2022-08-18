from drugportals.models import Portal
from utils.sitemaps import FullDomainGenericSitemap


sitemap = FullDomainGenericSitemap({
        'queryset': Portal.objects.all(),
    },
    priority=1.0,
    changefreq='daily',
    protocol='https'
)
sitemap.i18n = True


SITEMAPS = {
    'portals': sitemap,
}
