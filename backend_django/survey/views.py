# survey/views.py
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

from .serializers import SurveySerializer
from .utils import build_data_json, save_data_json
from ai.agent_runner import run_crewai_analysis, CrewAIExecutionError, CrewAIProgress

# 配置日志记录器
logger = logging.getLogger(__name__)

# 全局字典用于跟踪分析进度和结果
# 使用OrderedDict来限制字典大小，防止内存泄漏
from collections import OrderedDict
import threading

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


class SurveyView(APIView):
    """处理调查分析请求的视图"""
    def post(self, request):
        try:
            ser = SurveySerializer(data=request.data)
            if not ser.is_valid():
                return Response({"ok": False, "errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            data_dict = build_data_json(ser.validated_data)
            filename = request.query_params.get("filename")  # 可选：?filename=my_case
            file_path = save_data_json(data_dict, filename_stem=filename)

            # 生成分析ID，用于跟踪进度
            analysis_id = str(uuid.uuid4())
            
            # 使用全局锁确保进度和结果字典的初始化是原子操作
            with dictionaries_lock:
                # 初始化进度字典，避免后续查询时出现Not Found错误
                analysis_progress[analysis_id] = [{
                    'stage': 'initialization',
                    'progress': 0.0,
                    'message': '开始初始化分析',
                    'task_name': None,
                    'task_status': 'starting',
                    'timestamp': datetime.now().isoformat()
                }]
                
                # 初始化结果字典，确保即使在分析过程中查询也不会返回404
                analysis_results[analysis_id] = {
                    "ok": False,
                    "status": "processing",
                    "summary": None,
                    "report_markdown": None,
                    "report_path": None,
                    "tasks": None,
                    "error": None,
                    "progress_history": [],
                    "timestamp": datetime.now().isoformat()
                }
            
            # 在后台线程中启动分析
            thread = threading.Thread(
                target=start_async_analysis,
                args=(analysis_id, file_path),
                daemon=True
            )
            thread.start()
            
            # 立即返回响应，包含分析ID和状态检查的URL
            return Response({
                "ok": True,
                "message": "数据分析已开始，请轮询进度",
                "filename": file_path.name,
                "path": str(file_path),
                "analysis_id": analysis_id,
                "progress_url": f"/survey/progress/{analysis_id}/",
                "result_url": f"/survey/result/{analysis_id}/",
            })
        except Exception as e:
            logger.error(f"SurveyView处理请求失败: {str(e)}", exc_info=True)
            return Response({"ok": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalysisProgressView(APIView):
    """获取分析进度的视图"""
    def get(self, request, analysis_id):
        # 使用全局锁确保在检查和初始化字典时的线程安全
        with dictionaries_lock:
            # 如果分析ID不存在，初始化一个进度条目
            if analysis_id not in analysis_progress:
                analysis_progress[analysis_id] = [{
                    'stage': 'initialization',
                    'progress': 0.0,
                    'message': '分析尚未开始',
                    'task_name': None,
                    'task_status': 'not_started',
                    'timestamp': datetime.now().isoformat()
                }]
                
                # 同时初始化结果字典，确保一致性
                if analysis_id not in analysis_results:
                    analysis_results[analysis_id] = {
                        "ok": False,
                        "status": "processing",
                        "summary": None,
                        "report_markdown": None,
                        "report_path": None,
                        "tasks": None,
                        "error": None,
                        "progress_history": [],
                        "timestamp": datetime.now().isoformat()
                    }
            
            # 获取进度数据（在锁内完成以确保一致性）
            progress_data = analysis_progress[analysis_id].copy()
        
        # 在锁外处理数据和返回响应
        latest = progress_data[-1]
        return Response({
            "ok": True,
            "in_progress": latest['stage'] not in ['error', 'completed'],
            "progress": latest['progress'],
            "message": latest['message'],
            "details": progress_data,
            "analysis_id": analysis_id,
            "timestamp": latest.get('timestamp', datetime.now().isoformat())
        })


class AnalysisResultView(APIView):
    """获取分析结果的视图"""
    def get(self, request, analysis_id):
        # 使用全局锁确保在检查和初始化字典时的线程安全
        with dictionaries_lock:
            # 如果分析ID不存在，初始化一个处理中的状态，避免返回404错误
            if analysis_id not in analysis_results:
                # 检查是否有进度信息，说明任务正在执行但结果尚未保存
                progress_info = None
                if analysis_id in analysis_progress and analysis_progress[analysis_id]:
                    latest_progress = analysis_progress[analysis_id][-1]
                    progress_info = latest_progress.get('message', '分析正在进行中')
                else:
                    progress_info = '分析请求已接收，正在准备处理'
                    # 同时初始化进度字典
                    analysis_progress[analysis_id] = [{
                        'stage': 'initialization',
                        'progress': 0.0,
                        'message': progress_info,
                        'task_name': None,
                        'task_status': 'not_started',
                        'timestamp': datetime.now().isoformat()
                    }]
                
                # 初始化结果字典
                initial_analysis = {
                    "ok": False,
                    "status": "processing",
                    "summary": None,
                    "report_markdown": None,
                    "report_path": None,
                    "tasks": None,
                    "error": None,
                    "message": progress_info,
                    "progress_history": analysis_progress.get(analysis_id, []),
                    "timestamp": datetime.now().isoformat()
                }
                # 存储这个初始状态，避免后续请求再次返回404
                analysis_results[analysis_id] = initial_analysis
                
                # 返回初始状态响应
                return Response({
                    "ok": False,
                    "analysis": initial_analysis,
                    "message": progress_info
                }, status=status.HTTP_200_OK)
            
            # 获取结果的副本（在锁内完成以确保一致性）
            result = analysis_results[analysis_id].copy()
        # 根据结果的状态返回不同的响应
        if result.get("status") == "processing":
            # 获取最新进度信息
            progress_info = "分析正在进行中"
            if analysis_id in analysis_progress and analysis_progress[analysis_id]:
                latest_progress = analysis_progress[analysis_id][-1]
                progress_info = latest_progress.get('message', progress_info)
            return Response({
                "ok": False,
                "analysis": result,
                "message": progress_info,
                "analysis_id": analysis_id
            }, status=status.HTTP_200_OK)
        elif result.get("status") == "error" or result.get("error"):
            # 即使出错，也返回200状态码，但在响应体中表明错误状态
            return Response({
                "ok": False,
                "analysis": result,
                "message": "分析过程中遇到错误",
                "analysis_id": analysis_id
            }, status=status.HTTP_200_OK)
        else:
            # 成功完成的情况
            return Response({
                "ok": True,
                "analysis": result,
                "message": "分析成功完成",
                "analysis_id": analysis_id
            }, status=status.HTTP_200_OK)


# 异步任务执行器
async def execute_crewai_async(analysis_id, file_path):
    """异步执行CrewAI分析"""
    
    # 进度回调函数
    async def progress_callback(progress_info):
        # 使用全局锁保护progress字典的更新
        with dictionaries_lock:
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
    
    # 同步函数的异步包装器
    def progress_callback_sync(progress_info):
        # 在当前事件循环中创建任务，避免asyncio.run()导致的错误
        try:
            asyncio.create_task(progress_callback(progress_info))
        except Exception as e:
            # 如果当前没有运行的事件循环，使用线程执行
            def run_async_in_thread():
                try:
                    asyncio.run(progress_callback(progress_info))
                except Exception as inner_e:
                    logger.error(f"线程中异步回调失败: {inner_e}")
            threading.Thread(target=run_async_in_thread, daemon=True).start()
    
    # 初始化分析结果对象
    analysis = {
        "ok": False,
        "status": "error",  # 默认状态为错误，成功时会覆盖
        "summary": None,
        "report_markdown": None,
        "report_path": None,
        "tasks": None,
        "error": None,
        "progress_history": [],
        "timestamp": datetime.now().isoformat()
    }

    try:
        # 发送初始进度
        initial_progress = CrewAIProgress(
            stage="initialization",
            progress=0.1,
            message="开始CrewAI分析",
            task_status="starting"
        )
        await progress_callback(initial_progress)
        
        # 同步执行run_crewai_analysis，但提供进度回调
        crew_result = run_crewai_analysis(file_path, progress_callback=progress_callback_sync)
        
        # 更新进度为完成
        complete_progress = CrewAIProgress(
            stage="completed",
            progress=1.0,
            message="分析完成",
            task_status="completed"
        )
        await progress_callback(complete_progress)
        
        # 使用全局锁确保线程安全地更新分析结果
        with dictionaries_lock:
            # 更新分析结果
            analysis.update({
                "ok": bool(crew_result.summary or crew_result.report_markdown),
                "status": "completed" if crew_result.summary or crew_result.report_markdown else "partial",
                "summary": crew_result.summary,
                "report_markdown": crew_result.report_markdown,
                "report_path": crew_result.report_path,
                "tasks": crew_result.task_outputs,
                "error": None,
                "timestamp": datetime.now().isoformat()
            })
            # 合并现有进度历史，避免丢失
            if analysis_id in analysis_progress:
                analysis["progress_history"] = analysis_progress[analysis_id]
            # 保存结果
            analysis_results[analysis_id] = analysis
    except CrewAIExecutionError as exc:
        error_message = str(exc)
        logger.error(f"CrewAI执行错误: {error_message}")
        
        # 使用全局锁确保线程安全地更新错误状态
        with dictionaries_lock:
            analysis["error"] = error_message
            analysis["status"] = "error"
            
            # 更新进度为错误状态
            error_progress = CrewAIProgress(
                stage="error",
                progress=1.0,
                message=f"执行失败: {error_message}",
                task_status="error"
            )
            await progress_callback(error_progress)
    except Exception as e:  # 捕获所有其他异常，确保结果始终被更新
        error_message = f"未预期的错误: {str(e)}"
        logger.error(f"CrewAI分析过程中发生意外错误: {error_message}", exc_info=True)
        
        # 使用全局锁确保线程安全地更新错误状态
        with dictionaries_lock:
            analysis["error"] = error_message
            analysis["status"] = "error"
            
            # 更新进度为错误状态
            error_progress = CrewAIProgress(
                stage="error",
                progress=1.0,
                message=error_message,
                task_status="error"
            )
            await progress_callback(error_progress)
    finally:
        # 使用全局锁确保线程安全地更新最终结果
        with dictionaries_lock:
            # 确保在任何情况下都更新结果字典
            # 合并现有进度历史，避免丢失
            if analysis_id in analysis_progress:
                analysis["progress_history"] = analysis_progress[analysis_id]
            
            # 确保始终更新结果
            analysis_results[analysis_id] = analysis
            logger.info(f"分析任务 {analysis_id} 完成，状态: {analysis['status']}")


# 启动异步任务的辅助函数
def start_async_analysis(analysis_id, file_path):
    """启动异步分析任务"""
    loop = None
    try:
        # 确保日志记录
        logger.info(f"开始异步分析任务: {analysis_id}, 文件: {file_path}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(execute_crewai_async(analysis_id, file_path))
    except Exception as e:
        error_message = str(e)
        logger.error(f"异步分析执行失败: {error_message}", exc_info=True)
        
        # 使用全局锁确保线程安全地更新错误状态
        with dictionaries_lock:
            # 确保即使在异常情况下也更新进度和结果
            error_analysis = {
                "ok": False,
                "status": "error",
                "summary": None,
                "report_markdown": None,
                "report_path": None,
                "tasks": None,
                "error": error_message,
                "progress_history": [],
                "timestamp": datetime.now().isoformat()
            }
            analysis_results[analysis_id] = error_analysis
            
            # 更新进度为错误状态
            if analysis_id not in analysis_progress:
                analysis_progress[analysis_id] = []
            analysis_progress[analysis_id].append({
                'stage': 'error',
                'progress': 1.0,
                'message': f"执行失败: {error_message}",
                'task_name': None,
                'task_status': 'error',
                'timestamp': datetime.now().isoformat()
            })
            
            # 更新结果对象中的进度历史
            analysis_results[analysis_id]['progress_history'] = analysis_progress[analysis_id]
    finally:
        # 确保事件循环被正确关闭
        if loop:
            try:
                loop.close()
            except:
                pass

