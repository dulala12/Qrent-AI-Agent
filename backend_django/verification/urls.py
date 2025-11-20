# verification/urls.py - 验证码和邀请码相关的URL路由
from django.urls import path
from .views import validate_invitation, generate_new_invitation, get_invitation_status

urlpatterns = [
    # 验证邀请码
    path('validate/', validate_invitation, name='validate_invitation'),
    # 生成新的邀请码（管理接口）
    path('generate/', generate_new_invitation, name='generate_new_invitation'),
    # 获取邀请码状态
    path('status/<str:code>/', get_invitation_status, name='get_invitation_status'),
]