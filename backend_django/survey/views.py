# survey/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import asyncio
import json
import uuid
from pathlib import Path
from .serializers import SurveySerializer
from .utils import build_data_json, save_data_json
from .agent_runner import run_crewai_analysis, CrewAIExecutionError, CrewAIProgress

# 用于存储分析任务的进度
analysis_progress = {}

# 模拟WebSocket的进度更新机制
async def update_analysis_progress(analysis_id, progress_info):
    """更新分析任务的进度信息"""
    if analysis_id not in analysis_progress:
        analysis_progress[analysis_id] = []
    analysis_progress[analysis_id].append({
        'stage': progress_info.stage,
        'progress': progress_info.progress,
        'message': progress_info.message,
        'task_name': progress_info.task_name,
        'task_status': progress_info.task_status
    })

# 清除过期的进度信息
async def cleanup_progress():
    """定期清理过期的进度信息"""
    # 这里可以添加清理逻辑
    pass


class SurveyView(APIView):
    def post(self, request):
        ser = SurveySerializer(data=request.data)
        if not ser.is_valid():
            return Response({"ok": False, "errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
        data_dict = build_data_json(ser.validated_data)
        filename = request.query_params.get("filename")  # 可选：?filename=my_case
        file_path = save_data_json(data_dict, filename_stem=filename)

        # 生成分析ID，用于跟踪进度
        analysis_id = str(uuid.uuid4())
        
        # 立即返回一个响应，包含分析ID和状态检查的URL
        return Response({
            "ok": True,
            "message": "数据分析已开始，请轮询进度",
            "filename": file_path.name,
            "path": str(file_path),
            "analysis_id": analysis_id,
            "progress_url": f"/api/survey/progress/{analysis_id}",
            "result_url": f"/api/survey/result/{analysis_id}",
        })


class AnalysisProgressView(APIView):
    """获取分析进度的视图"""
    def get(self, request, analysis_id):
        if analysis_id not in analysis_progress:
            return Response({
                "ok": True,
                "in_progress": False,
                "progress": 0,
                "message": "分析尚未开始",
                "details": []
            })
        
        progress_data = analysis_progress[analysis_id]
        if not progress_data:
            return Response({
                "ok": True,
                "in_progress": True,
                "progress": 0,
                "message": "分析正在初始化",
                "details": []
            })
        
        latest = progress_data[-1]
        return Response({
            "ok": True,
            "in_progress": latest['stage'] not in ['error', 'completed'],
            "progress": latest['progress'],
            "message": latest['message'],
            "details": progress_data
        })


# 存储分析结果
analysis_results = {}


class AnalysisResultView(APIView):
    """获取分析结果的视图"""
    def get(self, request, analysis_id):
        if analysis_id not in analysis_results:
            return Response({
                "ok": False,
                "message": "结果尚未生成，请稍后再试"
            }, status=status.HTTP_404_NOT_FOUND)
        
        result = analysis_results[analysis_id]
        return Response({
            "ok": True,
            "analysis": result
        })


# 异步任务执行器
async def execute_crewai_async(analysis_id, file_path):
    """异步执行CrewAI分析"""
    
    # 进度回调函数
    async def progress_callback(progress_info):
        await update_analysis_progress(analysis_id, progress_info)
    
    # 同步函数的异步包装器
    def progress_callback_sync(progress_info):
        # 在当前事件循环中创建任务，避免asyncio.run()导致的错误
        try:
            asyncio.create_task(progress_callback(progress_info))
        except Exception as e:
            # 如果当前没有运行的事件循环，使用线程执行
            import threading
            def run_async_in_thread():
                try:
                    asyncio.run(progress_callback(progress_info))
                except Exception as inner_e:
                    print(f"线程中异步回调失败: {inner_e}")
            threading.Thread(target=run_async_in_thread, daemon=True).start()
    
    analysis = {
        "ok": False,
        "summary": None,
        "report_markdown": None,
        "report_path": None,
        "tasks": None,
        "error": None,
        "progress_history": []
    }

    try:
        # 同步执行run_crewai_analysis，但提供进度回调
        crew_result = run_crewai_analysis(file_path, progress_callback=progress_callback_sync)
        
        # 更新进度为完成
        complete_progress = CrewAIProgress(
            stage="completed",
            progress=1.0,
            message="分析完成",
            task_status="completed"
        )
        await update_analysis_progress(analysis_id, complete_progress)
        
        analysis.update(
            {
                "ok": bool(crew_result.summary or crew_result.report_markdown),
                "summary": crew_result.summary,
                "report_markdown": crew_result.report_markdown,
                "report_path": crew_result.report_path,
                "tasks": crew_result.task_outputs,
                "progress_history": [
                    {
                        'stage': p.stage,
                        'progress': p.progress,
                        'message': p.message,
                        'task_name': p.task_name,
                        'task_status': p.task_status
                    }
                    for p in crew_result.progress_history or []
                ]
            }
        )
    except CrewAIExecutionError as exc:
        error_message = str(exc)
        analysis["error"] = error_message
        # 更新进度为错误状态
        error_progress = CrewAIProgress(
            stage="error",
            progress=1.0,
            message=f"执行失败: {error_message}",
            task_status="error"
        )
        await update_analysis_progress(analysis_id, error_progress)
    
    # 存储结果
    analysis_results[analysis_id] = analysis


# 启动异步任务的辅助函数
def start_async_analysis(analysis_id, file_path):
    """启动异步分析任务"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(execute_crewai_async(analysis_id, file_path))
    except Exception as e:
        print(f"异步分析执行失败: {e}")
        # 确保即使在异常情况下也更新进度和结果
        error_analysis = {
            "ok": False,
            "summary": None,
            "report_markdown": None,
            "report_path": None,
            "tasks": None,
            "error": str(e),
            "progress_history": []
        }
        analysis_results[analysis_id] = error_analysis
        
        # 更新进度为错误状态
        if analysis_id not in analysis_progress:
            analysis_progress[analysis_id] = []
        analysis_progress[analysis_id].append({
            'stage': 'error',
            'progress': 1.0,
            'message': f"执行失败: {str(e)}",
            'task_name': None,
            'task_status': 'error'
        })
    finally:
        # 确保事件循环被正确关闭
        try:
            loop.close()
        except:
            pass


# 导入线程库，用于在后台运行分析
import threading

# 修改SurveyView的post方法，在后台启动分析
class SurveyView(APIView):
    def post(self, request):
        ser = SurveySerializer(data=request.data)
        if not ser.is_valid():
            return Response({"ok": False, "errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
        data_dict = build_data_json(ser.validated_data)
        filename = request.query_params.get("filename")  # 可选：?filename=my_case
        file_path = save_data_json(data_dict, filename_stem=filename)

        # 生成分析ID，用于跟踪进度
        analysis_id = str(uuid.uuid4())
        
        # 初始化进度
        analysis_progress[analysis_id] = [{
            'stage': 'initialization',
            'progress': 0.0,
            'message': '开始初始化分析',
            'task_name': None,
            'task_status': 'starting'
        }]
        
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

