from django.urls import path
from .views import SurveyView, AnalysisProgressView, AnalysisResultView

urlpatterns = [
    path('survey/', SurveyView.as_view(), name='survey'),
    path('progress/<str:analysis_id>/', AnalysisProgressView.as_view(), name='analysis_progress'),
    path('result/<str:analysis_id>/', AnalysisResultView.as_view(), name='analysis_result'),
]
