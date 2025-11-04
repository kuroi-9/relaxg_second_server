from django.urls import path
from .views import JobsManagerJobs

urlpatterns = [
    path('all/', JobsManagerJobs.as_view(), name='jobs-manager-jobs'),
]
