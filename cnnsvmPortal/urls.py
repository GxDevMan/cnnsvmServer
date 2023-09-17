from django.urls import path
from .views import aiInference, chat_filter

urlpatterns = [
    path('aiJudge/', aiInference),
    path('chatfilter/', chat_filter)
]