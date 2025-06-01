from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('version/', views.version, name='version'),
    path('temperature/', views.temperature, name='temperature'),
]