from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.flatpages.views import flatpage as flatpage_view
from django.contrib.sitemaps.views import sitemap as sitemap_view
from mixtures.sitemaps import SITEMAPS


def template(name, *args, **kwargs):
    return TemplateView.as_view(template_name=name, *args, **kwargs)

urlpatterns = [
    path('', include('drugcombinator.urls')),
    path('portail/', include('drugportals.urls')),
    path('robots.txt', template('mixtures/robots.txt', content_type='text/plain')),
    path('sitemap.xml', sitemap_view, {'sitemaps': SITEMAPS},
         name='django.contrib.sitemaps.views.sitemap'),
    path('admin/', admin.site.urls),
    # This provides backward compatibility for the "about" flatpage URL
    # reversing, becaiuse it used to be a TemplateView
    path('a-propos/', flatpage_view, {'url': '/a-propos/'}, name='about'),
    path('<path:url>/', flatpage_view, name='flatpage'),
]
