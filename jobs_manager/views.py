from django.http.response import JsonResponse
from django.http import FileResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from jobs_manager.services.jobs_manager_service import JobsManagerService
import json
from jobs_manager.serializers import JobsListSerializer

class JobsManagerJobs(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        jobs = jobsManagerService.get_jobs()
        serializer = JobsListSerializer(jobs, many=True)
        return Response(serializer.data)
