from celery import shared_task
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

@shared_task
def run_job_worker_task(job_data: dict):
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
    job_volumes_to_process = booksDBRepository.get_title_books_to_process(job_data['title_name'])
    job_volumes_names = [volume.name for volume in job_volumes_to_process]
    for volume in job_volumes_to_process:
        print(str(volume.name))

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

    for volume in job_volumes_to_process:
        volume_extraction_path = localFilesRepository.extraction(str(volume.title.name), str(volume.file_path))

        print("Running inference task")


        files_to_process = sorted([os.path.join(volume_extraction_path, f) for f in os.listdir(volume_extraction_path)])
        files_count = len(files_to_process)
        processed_files = 0
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
                    processed_files += 1
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
                processed_files += 1
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        'process_group',
                        {
                            'type': 'process.message',
                            'message': f'Inference | Image {str(processed_files)} already processed !'
                        }
                    )



def enhancement():
    pass
