from django.conf.urls import url
from django.urls import path
from . import views
 
urlpatterns = [
    path('',views.index),
    path('details',views.details),
    path('search',views.search),
]


