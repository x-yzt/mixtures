from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView


def template(name, *args, **kwargs):
    return TemplateView.as_view(template_name=name, *args, **kwargs)

urlpatterns = [
    path('', include('drugcombinator.urls')),
    path('portail/', include('drugportals.urls')),
    path('a-propos/', template('mixtures/about.html'), name='about'),
    path('robots.txt', template('mixtures/robots.txt', content_type='text/plain')),
    path('admin/', admin.site.urls)
]
