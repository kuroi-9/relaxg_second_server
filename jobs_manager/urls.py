from django.urls import path
from .views import JobsManagerJobs, JobsManagerInferenceTest, JobsManagerInference, JobsManagerJobsCreate

urlpatterns = [
    path('all/', JobsManagerJobs.as_view(), name='jobs-manager-jobs'),
    path('test/', JobsManagerInferenceTest.as_view(), name='jobs-manager-test'),
    path('inference/', JobsManagerInference.as_view(), name='jobs-manager-inference'),
    path('create/', JobsManagerJobsCreate.as_view(), name='jobs-manager-create'),
]
