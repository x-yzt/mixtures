from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap as sitemap_view

from mixtures.sitemaps import SITEMAPS
from utils.i18n import set_language_view


def template(name, *args, **kwargs):
    return TemplateView.as_view(template_name=name, *args, **kwargs)

urlpatterns = i18n_patterns(
    path('', include('drugcombinator.urls')),
    path('about/', template('mixtures/about.html'), name='about'),
    path('admin/', admin.site.urls),
)
urlpatterns += (
    path('setlang', set_language_view, name='set_language'),
    path('robots.txt', template('mixtures/robots.txt',
         content_type='text/plain')),
    path('sitemap.xml', sitemap_view, {'sitemaps': SITEMAPS},
         name='django.contrib.sitemaps.views.sitemap'),
)
