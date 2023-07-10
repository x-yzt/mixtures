from django.urls import path

from blog import views


urlpatterns = [
    path('',                     views.index,   name='index'),
    path('<int:page>',           views.index,   name='index'),
    path('article/<slug:slug>/', views.article, name='article'),
]
