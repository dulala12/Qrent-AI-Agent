# frontend/urls.py - 前端连接相关的路由
from django.urls import path
from .views import HealthCheckView, FrontendConfigView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('config/', FrontendConfigView.as_view(), name='frontend-config'),
]