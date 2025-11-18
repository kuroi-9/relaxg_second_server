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


        if not jobs_volumes_path:
            raise ValueError('Invalid job data')

        jobs_volumes_path = os.path.abspath(jobs_volumes_path)

        if not os.path.exists(jobs_volumes_path):
            raise FileNotFoundError('Job volume not found')

        if not os.path.isdir(jobs_volumes_path):
            raise NotADirectoryError('Job volume is not a directory')

        if not os.listdir(jobs_volumes_path):
            raise ValueError('Job volume is empty')


        run_inference_task.delay(job_data)
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'process_group',
                {
                    'type': 'process.message',
                    'message': 'Job worker started: ' + str(job_data['title_name']),
                }
            )
