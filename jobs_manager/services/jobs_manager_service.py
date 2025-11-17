import os
from typing import Dict, List, Any
from jobs_manager.models import Job
from jobs_manager.repositories.jobs_db_repository import JobsDBRepository
from jobs_manager.repositories.local_files_repository import LocalFilesRepository
from library.repositories.books_db_repository import BooksDBRepository
from jobs_manager.tasks import run_inference_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class JobsManagerService:
    def __init__(self, jobs_db_repo=JobsDBRepository, local_files_repo=LocalFilesRepository, books_db_repo=BooksDBRepository):
        self.jobsDBRepository = jobs_db_repo()
        self.localFilesRepository = local_files_repo()
        self.booksDBRepository = books_db_repo()

    def get_jobs(self) -> List[Job]:
        return self.jobsDBRepository.get_jobs()

    def get_job(self, job_id: int) -> Job:
        return self.jobsDBRepository.get_job(job_id)

    def create_job(self, job_data: Dict, upscale_params: Dict[str, Any] | None, user: Any) -> Job:
        return self.jobsDBRepository.create_job(job_data)

    def delete_job(self, job_id: int) -> bool:
        return self.jobsDBRepository.delete_job(job_id)

    def test_inference(self, job_data: Dict) -> None:
        '''Only for testing purposes'''
        return run_inference_task()

    def prepare_inference(self, job_data: Dict) -> None:
        '''
        Orchestrates the whole processing of a job.
        '''

        jobs_volumes_path = job_data['title_path']
        channel_layer = get_channel_layer()

        if not os.path.exists(jobs_volumes_path):
            raise FileNotFoundError(f"Directory {jobs_volumes_path} does not exist")

        # fetch the title books to work with, ordered
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'process_group',
                {
                    'type': 'process.message',
                    'message': 'Getting books'
                }
            )
        job_volumes_to_process = self.booksDBRepository.get_title_books_to_process(job_data['title_name'])
        job_volumes_names = [volume.name for volume in job_volumes_to_process]
        for volume in job_volumes_to_process:
            print(str(volume.name))

        # extracting books to process
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'process_group',
                {
                    'type': 'process.message',
                    'message': 'Found to process: ' + str(job_volumes_names),
                }
            )
        else:
            raise NotImplementedError("Channel layer is not available")

        for volume in job_volumes_to_process:
            self.localFilesRepository.extraction(jobs_volumes_path, str(volume.file_path))
            #todo: implement inference task in async with built-in django background tasks backend
            #run_inference_task()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    'process_group',
                    {
                        'type': 'process.message',
                        'message': 'Processing: ' + str(volume.name),
                    }
                )
            else:
                raise NotImplementedError("Channel layer is not available")
            break
