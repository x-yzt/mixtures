from django.urls import path, include
from drugcombinator import views


urlpatterns = [
    path('', views.main, name='main'),
]
