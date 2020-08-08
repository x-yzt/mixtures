from django.urls import path
from drugportals import views


urlpatterns = [
    path('<str:name>/', views.portal, name='portal'),
]
