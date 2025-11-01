# backend_django/limits/urls.py
from django.urls import path
from .views import (
    test_api,
    validate_invitation,
    generate_new_invitation,
    create_report,
    export_invitations,
    export_reports,
    create_test_invitation,
    fetch_and_save_limits
)

urlpatterns = [
    # 测试接口
    path('test/', test_api, name='test_api'),
    # 邀请码验证接口
    path('invitation/validate/', validate_invitation, name='validate_invitation'),
    # 生成新邀请码接口（管理用）
    path('invitation/generate/', generate_new_invitation, name='generate_new_invitation'),
    # 生成测试邀请码接口
    path('invitation/test/create/', create_test_invitation, name='create_test_invitation'),
    # 创建报告接口（会验证并使用邀请码）
    path('report/create/', create_report, name='create_report'),
    # 导出数据接口
    path('export/invitations/', export_invitations, name='export_invitations'),
    path('export/reports/', export_reports, name='export_reports'),
    # 原有接口
    path('update/', fetch_and_save_limits, name='fetch_and_save_limits'),
]