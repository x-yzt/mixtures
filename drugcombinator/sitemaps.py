from django.contrib.sitemaps import Sitemap, GenericSitemap
from django.urls import reverse
from drugcombinator.models import Interaction, Drug


class StaticSitemap(Sitemap):

    def __init__(self, pages, lastmod=None, priority=None,
            changefreq=None, protocol=None):
        self.pages = pages
        self.protocol = protocol
        
        self._lastmod = lastmod
        self._priority = priority
        self._changefreq = changefreq
    
    def items(self):
        return list(self.pages.keys())

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return self.pages[item].get('lastmod', self._lastmod)
    
    def priority(self, item):
        return self.pages[item].get('priority', self._priority)

    def changefreq(self, item):
        return self.pages[item].get('changefreq', self._changefreq)


pages_sitemap = StaticSitemap(
    {
        'main': {'priority': 1.0},
        'drug_search': {'priority': 0.7},
        'docs': {},
        'about': {}
    },
    priority = 0.5,
    changefreq = 'daily',
    protocol = 'https'
)

drugs_sitemap = GenericSitemap(
    {
        'queryset': Drug.objects.all(),
        'date_field': 'last_modified',
    },
    priority = 0.8,
    changefreq = 'daily',
    protocol = 'https'
)

interactions_sitemap = GenericSitemap(
    {
        'queryset': Interaction.objects.all(),
        'date_field': 'last_modified',
    },
    priority = 0.9,
    changefreq = 'daily',
    protocol = 'https'
)

SITEMAPS = {
    'pages': pages_sitemap,
    'drugs': drugs_sitemap,
    'interactions': interactions_sitemap
}
