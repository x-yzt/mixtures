from django.apps import apps
from django.contrib.sitemaps import Sitemap
from django.conf import settings
from django.urls import reverse
from importlib import import_module


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


def get_app_sitemaps():
    """
        Search for a `sitemaps` submodule in every app of the project.

        Each `sitemaps` submodule must contain a `SITEMAPS` dict
        containing the sitemaps e.g. `{'sitemap_name': sitemap_object}`.

        Sitemaps names are prefixed according to their `app_label`.
    """
    sitemaps = {}

    for app in apps.get_app_configs():
        try:
            app_sitemaps_module = import_module(f'{app.label}.sitemaps')
            app_sitemaps = app_sitemaps_module.SITEMAPS
        except (ImportError, AttributeError):
            continue # Having a sitemap submodule is not mandatory

        for name, sitemap in app_sitemaps.items():
            sitemaps[f'{app.label}.{name}'] = sitemap

    return sitemaps
