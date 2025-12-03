from celery import shared_task
from rg_server.celery import app
from inference_implementation.inference import InferenceImplementation
from jobs_manager.repositories.local_files_repository import LocalFilesRepository
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import os

from library.repositories.books_db_repository import BooksDBRepository
from jobs_manager.repositories.jobs_db_repository import JobsDBRepository
from library.serializers import BookDetailSerializer

inferenceImplementation = InferenceImplementation()
localFilesRepository = LocalFilesRepository()
booksDBRepository = BooksDBRepository()
jobsDBRepository = JobsDBRepository()

@shared_task(bind=True, track_started=True)
def calculate_job_progress(self, title_name: str) -> list:
    '''
    This function calculates the progress of a job based on the number of processed files.
    Intended to be used only to calculate the initial progress of a job.
    '''

    channel_layer = get_channel_layer()
    job_volumes_to_process = booksDBRepository.get_title_books_to_process(title_name)
    job_volumes_progress = [0] * len(job_volumes_to_process)
    for index, volume in enumerate(job_volumes_to_process):
        print(str(volume.name))
        if os.path.exists(f"/out/outputs/{volume.title.name}/{volume.name}"):
            if os.path.exists(f"/out/{volume.title.name}/{volume.name}"):
                current_volume_total_files = len(os.listdir(f"/out/{volume.title.name}/{volume.name}"))
                current_volume_processed_files = len(os.listdir(f"/out/outputs/{volume.title.name}/{volume.name}"))
                job_volumes_progress[index] = round(float((current_volume_processed_files / current_volume_total_files) * 100), 2)
            else:
                job_volumes_progress[index] = 0

    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'process_group',
            {
                'type': 'process.progress',
                'title_name': title_name,
                'percentages': job_volumes_progress,
                'step': 'Verifying'
            }
        )

    return job_volumes_progress

@app.task(bind=True, track_started=True)
def run_job_worker_task(self, job_data: dict):
    '''
    Orchestrate the whole processing of a job
    Run inference tasks
    '''

    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'process_group',
            {
                'type': 'process.message',
                'message': 'Job worker | Getting books'
            }
        )

    job_volumes_to_process = booksDBRepository.get_title_books_to_process(job_data["title_name"])
    job_volumes_names = [volume.name for volume in job_volumes_to_process]
    job_volumes_progress = calculate_job_progress(job_data["title_name"])

    # extracting books to process
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'process_group',
            {
                'type': 'process.message',
                'message': 'Job worker | Found to process: ' + str(job_volumes_names),
            }
        )
    else:
        raise NotImplementedError("Channel layer is not available")

    # HERE: Send process.progress message init progress status
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'process_group',
            {
                'type': 'process.progress',
                'title_name': job_data["title_name"],
                'percentages': job_volumes_progress,
                'step': 'Initializing'
            }
        )

    #=========
    # Per volume worker
    #=========
    for index, volume in enumerate(job_volumes_to_process):
        volume_extraction_path = localFilesRepository.extraction(str(volume.title.name), str(volume.file_path))

        print("Running inference task")


        files_to_process = sorted([os.path.join(volume_extraction_path, f) for f in os.listdir(volume_extraction_path)])
        current_volume_total_files = len(files_to_process)
        current_volume_processed_files = 0
        for image_full_path in files_to_process:
            image_name = os.path.splitext(os.path.basename(image_full_path))[0]
            if not os.path.exists(f"/out/outputs/{volume.title.name}/{volume.name}/{image_name} processed.jpg"):
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        'process_group',
                        {
                            'type': 'process.message',
                            'message': f'Inference | Processing image: {image_full_path}'
                        }
                    )
                inferenceImplementation.process_image(
                    image_full_path,
                    "/app/inference_implementation/4x-eula-digimanga-bw-v2-nc1.pth",
                    f"/out/outputs/{volume.title.name}/{volume.name}/{image_name} processed"
                )
                if os.path.exists(f"/out/outputs/{volume.title.name}/{volume.name}/{image_name} processed.jpg"):
                    # update job and book status etc
                    current_volume_processed_files += 1
                    serialized_book_data = BookDetailSerializer(volume).data
                    job_data['status'] = 'partial'
                    serialized_book_data['status'] = 'partial'
                    jobsDBRepository.update_job(job_data)
                    booksDBRepository.update_book(serialized_book_data)

                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            'process_group',
                            {
                                'type': 'process.message',
                                'message': f'Inference | Image processed !'
                            }
                        )
            else:
                current_volume_processed_files += 1
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        'process_group',
                        {
                            'type': 'process.message',
                            'message': f'Inference | Image {str(current_volume_processed_files)} already processed !'
                        }
                    )

            # HERE: Send process.progress message,
            # update progress status each files
            job_volumes_progress[index] = round(float((current_volume_processed_files / current_volume_total_files) * 100), 2)
            async_to_sync(channel_layer.group_send)(
                'process_group',
                {
                    'type': 'process.progress',
                    'title_name': job_data["title_name"],
                    'percentages': job_volumes_progress,
                    'step': 'Running'
                }
            )

@app.task(bind=True, track_started=True)
def process_success(self, unknown_arg, job_data):
    channel_layer = get_channel_layer()
    print(job_data)
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'process_group',
            {
                'type': 'process.success',
                'job_id': job_data["id"],
                'job_name': job_data["title_name"],
            }
        )

@app.task(bind=True, track_started=True)
def process_error(self, unknown_arg, job_data):
    channel_layer = get_channel_layer()
    print(job_data)
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'process_group',
            {
                'type': 'process.error',
                'job_id': job_data["id"],
                'job_name': job_data["title_name"],
            }
        )

def enhancement():
    pass
