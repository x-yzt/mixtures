from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView


template = lambda name: TemplateView.as_view(template_name=name)

urlpatterns = [
    path('', include('drugcombinator.urls')),
    path('a-propos/', template('mixtures/about.html'), name='about'),
    path('admin/', admin.site.urls)
]
