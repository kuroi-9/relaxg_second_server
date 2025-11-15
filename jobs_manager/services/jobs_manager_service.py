import os
from typing import Dict, List, Any
from jobs_manager.models import Job
from jobs_manager.repositories.jobs_db_repository import JobsDBRepository
from jobs_manager.repositories.local_files_repository import LocalFilesRepository
from jobs_manager.tasks import run_inference_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class JobsManagerService:
    def __init__(self, jobs_db_repo=JobsDBRepository, local_files_repo=LocalFilesRepository):
        self.jobsDBRepository = jobs_db_repo()
        self.localFilesRepository = local_files_repo()

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

    def process_controller(self, job_data: Dict) -> None:
        '''
        Orchestrates the whole processing of a job.
        '''

        jobs_volumes_path = job_data['title_path']
        channel_layer = get_channel_layer()

        if not os.path.exists(jobs_volumes_path):
            raise FileNotFoundError(f"Directory {jobs_volumes_path} does not exist")

        # scanning available volumes of the title
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'process_group',
                {
                    'type': 'process.message',
                    'message': 'Scanning books'
                }
            )
        jobs_volumes = self.localFilesRepository.scan(jobs_volumes_path)
        print(jobs_volumes)

        # extracting books
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'process_group',
                {
                    'type': 'process.message',
                    'message': 'Extracting books'
                }
            )
        else:
            raise NotImplementedError("Channel layer is not available")

        for job_volume in jobs_volumes:
            self.localFilesRepository.extraction(job_data['title_name'], job_volume)
            break
