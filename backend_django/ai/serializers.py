# ai/serializers.py - AI分析相关的数据序列化器
from rest_framework import serializers
from typing import Dict, Any, Optional

class SurveyAnalysisSerializer(serializers.Serializer):
    """问卷分析请求序列化器"""
    renting_requirements = serializers.DictField(required=True, help_text="租赁需求信息")
    analysis_type = serializers.CharField(default="comprehensive", help_text="分析类型")
    # 可以添加更多的字段验证和处理
    
    def validate_renting_requirements(self, value):
        """验证租赁需求数据"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("租赁需求必须是JSON对象")
        # 可以添加更详细的验证逻辑
        return value
    
    def to_internal_value(self, data):
        """转换外部数据到内部表示"""
        # 支持直接传递租赁需求作为根对象的情况
        if isinstance(data, dict) and 'renting_requirements' not in data:
            # 如果没有renting_requirements字段，则将整个数据作为租赁需求
            return {
                'renting_requirements': data,
                'analysis_type': data.get('analysis_type', 'comprehensive')
            }
        return super().to_internal_value(data)

class AnalysisProgressSerializer(serializers.Serializer):
    """分析进度序列化器"""
    analysis_id = serializers.CharField(read_only=True, help_text="分析ID")
    stage = serializers.CharField(read_only=True, help_text="当前阶段")
    progress = serializers.FloatField(read_only=True, help_text="进度百分比")
    message = serializers.CharField(read_only=True, help_text="状态消息")
    task_name = serializers.CharField(read_only=True, allow_null=True, help_text="当前任务名称")
    task_status = serializers.CharField(read_only=True, allow_null=True, help_text="任务状态")
    is_completed = serializers.BooleanField(read_only=True, help_text="是否完成")

class AnalysisResultSerializer(serializers.Serializer):
    """分析结果序列化器"""
    analysis_id = serializers.CharField(read_only=True, help_text="分析ID")
    summary = serializers.CharField(read_only=True, allow_null=True, help_text="分析摘要")
    report_markdown = serializers.CharField(read_only=True, allow_null=True, help_text="报告内容")
    task_outputs = serializers.DictField(read_only=True, allow_null=True, help_text="各任务输出")
    progress_history = AnalysisProgressSerializer(read_only=True, many=True, allow_null=True, help_text="进度历史")
    created_at = serializers.DateTimeField(read_only=True, help_text="创建时间")
    completed_at = serializers.DateTimeField(read_only=True, allow_null=True, help_text="完成时间")

class ErrorResponseSerializer(serializers.Serializer):
    """错误响应序列化器"""
    error = serializers.CharField(help_text="错误信息")
    code = serializers.IntegerField(default=400, help_text="错误代码")
    details = serializers.DictField(allow_null=True, help_text="详细信息")