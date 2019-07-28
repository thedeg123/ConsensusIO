from django.contrib import admin
from django.urls import path
from . import views

app_name='web'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('acknowledgments/', views.acknowledgments, name='acknowledgments'),
]
