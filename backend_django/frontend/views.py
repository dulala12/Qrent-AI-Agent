# frontend/views.py - 前端连接相关的视图
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """健康检查视图，用于验证后端服务是否正常运行"""
    def get(self, request):
        return Response({
            "ok": True,
            "message": "服务正常运行",
            "version": "1.0.0"
        })


class FrontendConfigView(APIView):
    """提供前端配置信息的视图"""
    def get(self, request):
        try:
            config = {
                "api_version": "v1",
                "supported_features": [
                    "survey_analysis",
                    "real_time_progress",
                    "result_retrieval"
                ],
                "service_status": "operational"
            }
            return Response({
                "ok": True,
                "config": config
            })
        except Exception as e:
            logger.error(f"获取前端配置时发生错误: {str(e)}")
            return Response({
                "ok": False,
                "error": "获取配置失败"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)