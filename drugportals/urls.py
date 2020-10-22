from django.urls import path
from drugportals import views


urlpatterns = [
    path('', views.portal, name='portal'),
]
