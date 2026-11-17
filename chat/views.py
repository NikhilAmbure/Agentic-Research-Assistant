	# HTTP layer: validates input, 
    # throttles, creates the thread_id, queues the task, reads the status

import uuid

from django.core.cache import cache

from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from .serializers import ReviewSerializer, StartSerializer

from agent.service import research_status

from .tasks import resume_research, run_research


class ResearchStartThrottle(AnonRateThrottle):
    scope = "research_start"


class ResearchStartView(APIView):
    throttle_classes = [ResearchStartThrottle]

    def post(self, request):
        s = StartSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        thread_id = str(uuid.uuid4())
        cache.set(f"research:{thread_id}", 1, 3600)
        run_research.delay(thread_id, s.validated_data["topic"])
        return Response({"thread_id": thread_id, "status": "queued"}, status=202)


class ResearchDetailView(APIView):
    def get(self, request, thread_id):
        info = research_status(str(thread_id))
        if info is None:
            return Response({"detail": "Unknown thread_id"}, status=404)
        return Response({"thread_id": str(thread_id), **info})


class ResearchReviewView(APIView):
    def post(self, request, thread_id):
        s = ReviewSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        info = research_status(str(thread_id))
        if info is None:
            return Response({"detail": "Unknown thread_id"}, status=404)
        if info["status"] != "awaiting_review":
            return Response({"detail": "Not awaiting review", "status": info["status"]}, status=409)
        resume_research.delay(str(thread_id), s.validated_data["action"], s.validated_data.get("feedback", ""))
        return Response({"thread_id": str(thread_id), "status": "running"}, status=202)