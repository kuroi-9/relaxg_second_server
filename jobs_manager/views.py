from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http.response import JsonResponse
from rest_framework.permissions import IsAuthenticated
from jobs_manager.services.jobs_manager_service import JobsManagerService
from jobs_manager.serializers import JobsListSerializer, JobSerializer, JobPreviewSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class JobsManagerJobs(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        jobs = jobsManagerService.get_jobs()
        serializer = JobsListSerializer(jobs, many=True)
        return Response(serializer.data)

class JobsManagerJobsProgress(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        if jobsManagerService.get_jobs_progress():
            return Response(status=200)
        return Response(status=500)

class JobsManagerJobsCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        jobsManagerService.create_job(request.data, {}, None)
        return Response(status=201)

class JobsManagerJobsDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, job_id: int, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        jobsManagerService.delete_job(job_id)
        return Response(status=200)

class JobsManagerInferenceTest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        jobsManagerService.test_inference(request.data)
        return Response(status=200)

class JobsManagerGetJobStatus(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request, job_id: int, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        res = jobsManagerService.get_job_status(job_id)
        return Response({'status': res}, status=200)

class JobsManagerStopJob(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, job_id: int, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        res = jobsManagerService.stop_job(job_id)
        return Response({'status': res}, status=200)

class JobsManagerInference(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs) -> Response:
        jobsManagerService = JobsManagerService()
        job = jobsManagerService.get_job(request.data['id'])
        job_serialized = JobPreviewSerializer(job)

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'process_group',
                {
                    'type': 'process.message',
                    'message': 'Preparing job worker'
                }
            )

        isPrepared = jobsManagerService.prepare_job_worker(job_serialized.data)
        if isPrepared:
            # we should return 202 when it will be async? don't know yet
            return Response(status=202)
        else:
            return Response({'error': 'Failed to prepare job worker'}, status=500)
