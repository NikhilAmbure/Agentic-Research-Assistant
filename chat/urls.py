from django.urls import path
from . import views

urlpatterns = [
    path("research/", views.ResearchStartView.as_view()),
    path("research/<uuid:thread_id>/", views.ResearchDetailView.as_view()),
    path("research/<uuid:thread_id>/review/", views.ResearchReviewView.as_view()),
]