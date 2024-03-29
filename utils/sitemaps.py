import re
from importlib import import_module

from django.apps import apps
from django.contrib.sitemaps import GenericSitemap, Sitemap
from django.urls import reverse


class StaticSitemap(Sitemap):
    """This `Sitemap` subclasses allows a dict as first argument, where
    keys are URL identifiers and values are dicts of parameters.

    If no parameter page-specific parameter is specified, default values
    from the class constructor will be used.
    """
    def __init__(self, pages, lastmod=None, priority=None,
                 changefreq=None, protocol=None, i18n=False):
        self.pages = pages
        self.protocol = protocol

        self._lastmod = lastmod
        self._priority = priority
        self._changefreq = changefreq
        self._i18n = i18n

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

    def i18n(self, item):
        return self.pages[item].get('i18n', self.i18n)


class FullDomainSitemapMixin:
    """This mixin is intended to work with `Sitemap` or
    `GenericSitemap`, and allows use with objects which the `location`
    already contains a full domain.

    This is useful when dealing when multidomain sites, e.g. when
    using the `django-host` package.
    """
    def location(self, *args):
        # The reversed URL may contain an unwanted domain scheme
        url = super().location(*args)
        # Strip 'http://', 'https://' or '//'
        return re.sub(r'^(https?:)?//', '', url)

    def _urls(self, page, protocol, domain):
        # Null the domain, because it is already part of location
        return super()._urls(page, protocol, domain='')


class FullDomainGenericSitemap(FullDomainSitemapMixin, GenericSitemap):
    pass


def get_app_sitemaps():
    """Search for a `sitemaps` submodule in every app of the project.

    Each `sitemaps` submodule must contain a `SITEMAPS` dict containing
    the sitemaps e.g. `{'sitemap_name': sitemap_object}`.

    Sitemaps names are prefixed according to their `app_label`.
    """
    sitemaps = {}

    for app in apps.get_app_configs():
        try:
            app_sitemaps_module = import_module(f'{app.label}.sitemaps')
            app_sitemaps = app_sitemaps_module.SITEMAPS
        except (ImportError, AttributeError):
            continue  # Having a sitemap submodule is not mandatory

        for name, sitemap in app_sitemaps.items():
            sitemaps[f'{app.label}.{name}'] = sitemap

    return sitemaps
