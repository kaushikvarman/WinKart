from django.urls import path 
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    # angle brackets are used to retrieve data from url to views
    # https://docs.djangoproject.com/en/4.2/topics/http/urls/#how-django-processes-a-request
    path('<slug:category_slug>/', views.store, name='products_by_category'),
  
    

]