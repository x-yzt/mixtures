from django.urls import include, path, register_converter
from drugcombinator.converters import SlugListConverter
from drugcombinator.api import views


register_converter(SlugListConverter, 'slug_list')

urlpatterns = [
    path('v1/', include([
        path('aliases/', views.aliases, name='aliases'),
        path('substances/', views.drugs, name='drugs'),
        path('substance/<slug:slug>/', views.drug, name='drug'),
        path('combo/<slug_list:slugs>/', views.combine, name='combine'),
    ])),
]
