from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap as sitemap_view
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from mixtures.sitemaps import SITEMAPS
from utils.i18n import set_language_view
from utils.urls import template


urlpatterns = i18n_patterns(
    path('', include('drugcombinator.urls')),
    path('admin/', admin.site.urls),
    path('i18n.js', JavaScriptCatalog.as_view(), name='i18n'),
)
urlpatterns += (
    path('setlang', set_language_view, name='set_language'),
    path(
        'robots.txt',
        template('mixtures/robots.txt', content_type='text/plain')),
    path(
        'sitemap.xml',
        sitemap_view, {'sitemaps': SITEMAPS},
        name='django.contrib.sitemaps.views.sitemap'),
)
