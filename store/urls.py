from django.urls import path 
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    # angle brackets are used to retrieve data from url to views
    # https://docs.djangoproject.com/en/4.2/topics/http/urls/#how-django-processes-a-request
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/',views.search,name='search' ),

    path('submit_reviews/<int:product_id>/',views.submit_reviews,name='submit_reviews'),
  
    

]