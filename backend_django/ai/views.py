# ai/views.py - AI分析相关的视图
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import asyncio
import json
import uuid
from pathlib import Path
import threading
from datetime import datetime
import logging

from .serializers import SurveyAnalysisSerializer, AnalysisProgressSerializer, AnalysisResultSerializer
from .utils import build_data_json, save_data_json
from .agent_runner import run_crewai_analysis, CrewAIExecutionError, CrewAIProgress

# 配置日志记录器
logger = logging.getLogger(__name__)

# 全局字典用于跟踪分析进度和结果
# 使用OrderedDict来限制字典大小，防止内存泄漏
from collections import OrderedDict

class LimitedSizeDict(OrderedDict):
    """有限大小的字典，当达到最大容量时自动删除最早的条目"""
    def __init__(self, max_size=100):
        super().__init__()
        self.max_size = max_size
        self.lock = threading.RLock()  # 添加锁以确保线程安全

    def __setitem__(self, key, value):
        with self.lock:
            # 如果达到最大容量，删除最早添加的项
            if key not in self and len(self) >= self.max_size:
                self.popitem(last=False)
            super().__setitem__(key, value)
    
    def __getitem__(self, key):
        with self.lock:
            return super().__getitem__(key)
    
    def __contains__(self, key):
        with self.lock:
            return super().__contains__(key)
    
    def get(self, key, default=None):
        with self.lock:
            return super().get(key, default)

# 创建有限大小的字典，最大存储100个条目
analysis_progress = LimitedSizeDict(max_size=100)
analysis_results = LimitedSizeDict(max_size=100)

# 全局锁用于复杂操作的原子性
dictionaries_lock = threading.RLock()

# 模拟WebSocket的进度更新机制
async def update_analysis_progress(analysis_id, progress_info):
    """更新分析任务的进度信息"""
    if analysis_id not in analysis_progress:
        analysis_progress[analysis_id] = []
    progress_entry = {
        'stage': progress_info.stage,
        'progress': progress_info.progress,
        'message': progress_info.message,
        'task_name': progress_info.task_name,
        'task_status': progress_info.task_status,
        'timestamp': datetime.now().isoformat()
    }
    analysis_progress[analysis_id].append(progress_entry)
    
    # 同步更新结果字典中的状态
    if analysis_id in analysis_results:
        analysis_results[analysis_id]['status'] = 'processing'
        analysis_results[analysis_id]['timestamp'] = datetime.now().isoformat()

# 清除过期的进度信息
async def cleanup_progress():
    """定期清理过期的进度信息"""
    # 这里可以添加清理逻辑
    pass


class AnalysisProgressView(APIView):
    """获取分析任务的进度信息"""
    def get(self, request, analysis_id):
        try:
            if analysis_id not in analysis_progress:
                return Response({
                    "status": "error",
                    "error": "分析ID不存在或已过期"
                }, status=status.HTTP_404_NOT_FOUND)
            
            progress = analysis_progress[analysis_id]
            # 使用序列化器格式化响应数据
            progress_data = {
                "analysis_id": analysis_id,
                "stage": progress.get("stage", "unknown"),
                "progress": progress.get("progress", 0),
                "message": progress.get("message", ""),
                "task_name": progress.get("task_name"),
                "task_status": progress.get("task_status"),
                "is_completed": progress.get("progress", 0) >= 1.0
            }
            serializer = AnalysisProgressSerializer(progress_data)
            return Response({
                "status": "success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"获取分析进度时发生错误: {str(e)}")
            return Response({
                "status": "error",
                "error": "获取分析进度失败"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalysisResultView(APIView):
    """获取分析结果的视图"""
    def get(self, request, analysis_id):
        try:
            if analysis_id not in analysis_results:
                return Response({
                    "status": "error",
                    "error": "分析ID不存在或已过期"
                }, status=status.HTTP_404_NOT_FOUND)
            
            analysis_data = analysis_results[analysis_id]
            # 使用序列化器格式化响应数据
            result_data = {
                "analysis_id": analysis_id,
                "summary": analysis_data.get("result", {}).get("summary"),
                "report_markdown": analysis_data.get("result", {}).get("report"),
                "task_outputs": analysis_data.get("result", {}).get("task_outputs"),
                "progress_history": analysis_progress.get(analysis_id),
                "created_at": analysis_data.get("timestamp"),
                "completed_at": analysis_data.get("timestamp") if analysis_data.get("status") == "completed" else None
            }
            serializer = AnalysisResultSerializer(result_data)
            return Response({
                "status": "success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"获取分析结果时发生错误: {str(e)}")
            return Response({
                "status": "error",
                "error": "获取分析结果失败"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SurveyAnalysisView(APIView):
    """处理调查分析请求的视图"""
    def post(self, request):
        try:
            ser = SurveyAnalysisSerializer(data=request.data)
            if not ser.is_valid():
                return Response({"ok": False, "errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            data_dict = build_data_json(ser.validated_data)
            filename = request.query_params.get("filename")  # 可选：?filename=my_case
            file_path = save_data_json(data_dict, filename_stem=filename)

            # 生成分析ID，用于跟踪进度
            analysis_id = str(uuid.uuid4())
            
            # 使用全局锁确保进度和结果字典的初始化是原子操作
            with dictionaries_lock:
                analysis_progress[analysis_id] = []
                analysis_results[analysis_id] = {
                    "analysis_id": analysis_id,
                    "status": "started",
                    "file_path": str(file_path),
                    "timestamp": datetime.now().isoformat(),
                    "result": None
                }
            
            # 异步启动分析任务
            asyncio.create_task(execute_crewai_async(analysis_id, file_path))
            
            return Response({
                "ok": True,
                "analysis_id": analysis_id,
                "message": "分析已开始，请定期查询进度"
            })
        except Exception as e:
            logger.error(f"处理调查分析请求时发生错误: {str(e)}")
            return Response({
                "ok": False,
                "error": "创建分析任务失败"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def execute_crewai_async(analysis_id, file_path):
    """异步执行CrewAI分析"""
    try:
        # 更新进度为开始处理
        await update_analysis_progress(
            analysis_id,
            CrewAIProgress(
                stage="preprocessing",
                progress=0.0,
                message="开始处理分析请求",
                task_name="初始化分析",
                task_status="in_progress"
            )
        )
        
        # 读取数据文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 更新进度
        await update_analysis_progress(
            analysis_id,
            CrewAIProgress(
                stage="processing",
                progress=0.2,
                message="数据文件读取完成，开始AI分析",
                task_name="数据准备",
                task_status="completed"
            )
        )
        
        # 执行CrewAI分析 - 使用线程池运行同步函数
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,  # 使用默认线程池
            lambda: run_crewai_analysis(
                file_path,  # 注意：这里应该传递文件路径，而不是数据
                progress_callback=lambda progress: asyncio.run_coroutine_threadsafe(
                    update_analysis_progress(analysis_id, progress), loop
                )
            )
        )
        
        # 更新结果
        with dictionaries_lock:
            analysis_results[analysis_id].update({
                "status": "completed",
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
        
        # 最后更新一次进度
        await update_analysis_progress(
            analysis_id,
            CrewAIProgress(
                stage="completed",
                progress=1.0,
                message="分析完成",
                task_name="AI分析",
                task_status="completed"
            )
        )
        
    except CrewAIExecutionError as e:
        logger.error(f"CrewAI分析执行错误: {str(e)}")
        with dictionaries_lock:
            analysis_results[analysis_id].update({
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        await update_analysis_progress(
            analysis_id,
            CrewAIProgress(
                stage="failed",
                progress=0.0,
                message=f"分析失败: {str(e)}",
                task_name="AI分析",
                task_status="failed"
            )
        )
    except Exception as e:
        logger.error(f"异步执行分析时发生未知错误: {str(e)}")
        with dictionaries_lock:
            analysis_results[analysis_id].update({
                "status": "failed",
                "error": f"内部错误: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        
        await update_analysis_progress(
            analysis_id,
            CrewAIProgress(
                stage="failed",
                progress=0.0,
                message=f"分析失败: 内部错误",
                task_name="AI分析",
                task_status="failed"
            )
        )