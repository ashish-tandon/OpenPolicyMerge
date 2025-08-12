"""
URL configuration for api app.
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('health/', views.health, name='health'),
    path('status/', views.status, name='status'),
]