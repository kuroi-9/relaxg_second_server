from django.urls import path
from .views import JobsManagerJobs, JobsManagerJobsInference

urlpatterns = [
    path('all/', JobsManagerJobs.as_view(), name='jobs-manager-jobs'),
    path('test/', JobsManagerJobsInference.as_view(), name='jobs-manager-test'),
]
