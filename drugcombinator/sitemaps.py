from django.contrib.sitemaps import GenericSitemap

from drugcombinator.models import Drug, Interaction
from utils.sitemaps import StaticSitemap


pages_sitemap = StaticSitemap({
        'main': {'priority': 1.0},
        'drug_search': {'priority': 0.7},
        'docs': {},
    },
    priority=0.5,
    changefreq='daily',
    protocol='https',
    i18n=True
)

drugs_sitemap = GenericSitemap({
        'queryset': Drug.objects.all(),
        'date_field': 'last_modified',
    },
    priority=0.8,
    changefreq='daily',
    protocol='https'
)
drugs_sitemap.i18n = True

interactions_sitemap = GenericSitemap({
        'queryset': Interaction.objects.all(),
        'date_field': 'last_modified',
    },
    priority=0.9,
    changefreq='daily',
    protocol='https'
)
interactions_sitemap.i18n = True

SITEMAPS = {
    'pages': pages_sitemap,
    'drugs': drugs_sitemap,
    'interactions': interactions_sitemap
}
