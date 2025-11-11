from celery import shared_task
from django.conf import settings

from inference_implementation.inference import InferenceImplementation
from jobs_manager.repositories.local_files_repository import LocalFilesRepository

inferenceImplementation = InferenceImplementation()
localFilesRepository = LocalFilesRepository()

@shared_task
def run_inference_task():
    inferenceImplementation.process_image("/app/inference_implementation/frieren-beyond-5120x2880-22999.jpg", "/app/inference_implementation/4x-eula-digimanga-bw-v2-nc1.pth", "/app/inference_implementation/output_inf")

def enhancement():
    pass
