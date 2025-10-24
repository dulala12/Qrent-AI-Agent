from django.urls import path
from .views import SurveyView

urlpatterns = [
    path("survey", SurveyView.as_view()),
]
