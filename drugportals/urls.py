from django.urls import path
from drugportals import views


urlpatterns = [
    path('<str:drug>/', views.portal, name='portal'),
]
