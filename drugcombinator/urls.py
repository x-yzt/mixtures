from django.urls import path, include, register_converter
from django.views.decorators.cache import cache_page
from django.contrib.sitemaps.views import sitemap as sitemap_view
from drugcombinator.converters import SlugListConverter
from drugcombinator import views
from drugcombinator.sitemaps import SITEMAPS


cache = cache_page(60 * 10)

register_converter(SlugListConverter, 'slug_list')

urlpatterns = [
    path('', views.main, name='main'),
    path('combo/<slug_list:slugs>/', views.combine, name='combine'),
    path('substance/<str:name>/', views.DrugView.as_view(), name='drug'),
    path('substances/', views.drug_search, name='drug_search'),
    path('table/', views.table, name='table'),
    path('table/<slug_list:slugs>/', views.table, name='table'),
    path('docs/', views.docs, name='docs'),

    path('sitemap.xml', sitemap_view, {'sitemaps': SITEMAPS},
         name='django.contrib.sitemaps.views.sitemap'),

    path('autocomplete.js', cache(views.autocomplete), name='autocomplete')
]
