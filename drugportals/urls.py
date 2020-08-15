from django.urls import path
from drugportals import views


urlpatterns = [
    path('<slug:drug>/', views.portal, name='portal'),
]
