from django.urls import include, path

from drugcombinator.api import views


app_name = 'api'

urlpatterns = [
    path('v1/', include([
        path('aliases/',                 views.aliases, name='aliases'),
        path('search/<str:name>/',       views.search,  name='search'),
        path('substances/',              views.drugs,   name='drugs'),
        path('substance/<slug:slug>/',   views.drug,    name='drug'),
        path('combo/<slug_list:slugs>/', views.combine, name='combine'),
    ])),
]
