from django.urls import path
from .views import ChatView, ChatStreamView, HistoryView, HealthView

urlpatterns = [
    path("chat/",               ChatView.as_view(),       name="chat"),
    path("chat/stream/",        ChatStreamView.as_view(), name="chat-stream"),
    path("history/<str:session_id>/", HistoryView.as_view(),  name="history"),
    path("health/",             HealthView.as_view(),     name="health"),
]