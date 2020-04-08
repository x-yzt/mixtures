from django.urls import path, include, register_converter
from django.views.decorators.cache import cache_page
from drugcombinator.converters import SlugListConverter
from drugcombinator import views


register_converter(SlugListConverter, 'slug_list')

urlpatterns = [
    path('', views.main, name='main'),
    path('combo/<slug_list:slugs>/', views.combine, name='combine'),
    path('substance/<str:name>/', views.drug, name='drug'),
    path('substances/', views.drug_search, name='drug_search'),

    path('autocomplete.js', cache_page(60 * 10)(views.autocomplete), name='autocomplete')
]
