# backend_django/limits/urls.py
from django.urls import path
#from .views import fetch_and_save_limits
from .views import test_api

urlpatterns = [
    #path('update/', fetch_and_save_limits, name='fetch_and_save_limits'),
    path('test/', test_api, name='test_api'),
]