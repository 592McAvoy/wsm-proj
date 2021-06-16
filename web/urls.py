from django.conf.urls import url
from django.urls import path
from . import views
 
urlpatterns = [
    # url(r'^$', views.hello),
    # path('hello/', views.hello),
    path('',views.index),
    path('details',views.details),
    # path('details_instrument',views.details_instrument),
    path('search',views.search),
    path('sort',views.sort)
]


