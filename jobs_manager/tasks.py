from celery import shared_task
from inference_implementation.inference import InferenceImplementation
from jobs_manager.repositories.local_files_repository import LocalFilesRepository
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

inferenceImplementation = InferenceImplementation()
localFilesRepository = LocalFilesRepository()

@shared_task
def run_inference_task():
    print("Running inference task")
    inferenceImplementation.process_image("/app/inference_implementation/frieren-beyond-5120x2880-22999.jpg", "/app/inference_implementation/4x-eula-digimanga-bw-v2-nc1.pth", "/app/inference_implementation/output_inf")
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'process_group',
            {
                'type': 'process.message',
                'message': 'Image processed'
            }
        )


def enhancement():
    pass
