from django.urls import path, register_converter
from django.views.decorators.cache import cache_page

from drugcombinator import views
from drugcombinator.converters import SlugListConverter


cache = cache_page(60 * 10)

register_converter(SlugListConverter, 'slug_list')

urlpatterns = [
    path('',                         views.main,                name='main'),
    path('combo/<slug_list:slugs>/', views.combine,             name='combine'),
    path('substance/<str:name>/',    views.DrugView.as_view(),  name='drug'),
    path('substances/',              views.drug_search,         name='drug_search'),
    path('recap/<str:name>/',        views.RecapView.as_view(), name='recap'),
    path('table/',                   views.table,               name='table'),
    path('table/<slug_list:slugs>/', views.table,               name='table'),
    path('about/',                   views.about,               name='about'),
    path('docs/',                    views.docs,                name='docs'),

    path('send-contrib/',            views.send_contrib,        name='send_contrib'),
    path('autocomplete.js',          cache(views.autocomplete), name='autocomplete'),
]
