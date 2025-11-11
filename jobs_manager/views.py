from django.http.response import JsonResponse
from django.http import FileResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from jobs_manager.services.jobs_manager_service import JobsManagerService
import json
from jobs_manager.serializers import JobsListSerializer, JobSerializer

class JobsManagerJobs(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        jobs = jobsManagerService.get_jobs()
        serializer = JobsListSerializer(jobs, many=True)
        return Response(serializer.data)

class JobsManagerJobsCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        jobsManagerService.create_job(request.data, {}, None)
        return Response(status=201)

class JobsManagerInferenceTest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        jobsManagerService.test_inference(request.data)
        return Response(status=201)

class JobsManagerInference(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        #its job id, and we need to fetch the title path HERE
        job = jobsManagerService.get_job(request.data['id'])
        job_serialized = JobSerializer(job)
        print(job_serialized.data)
        jobsManagerService.process_controller(job_serialized.data)
        return Response(status=201)
