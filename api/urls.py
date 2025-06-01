from django.urls import path
from . import views  # You'll need to create this views.py file too

urlpatterns = [
    path('version/', views.version, name='version'),
    path('temperature/', views.temperature, name='temperature'),
]