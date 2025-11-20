# ai/urls.py - AI分析相关的路由
from django.urls import path
from .views import SurveyAnalysisView, AnalysisProgressView, AnalysisResultView

urlpatterns = [
    path('analysis/', SurveyAnalysisView.as_view(), name='survey-analysis'),
    path('analysis/progress/<str:analysis_id>/', AnalysisProgressView.as_view(), name='analysis-progress'),
    path('analysis/result/<str:analysis_id>/', AnalysisResultView.as_view(), name='analysis-result'),
]