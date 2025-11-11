from typing import Dict, List, Any
from jobs_manager.models import Job
from jobs_manager.repositories.jobs_db_repository import JobsDBRepository
from jobs_manager.repositories.local_files_repository import LocalFilesRepository
from jobs_manager.tasks import run_inference_task
import os

class JobsManagerService:
    def __init__(self, jobs_db_repo=JobsDBRepository, local_files_repo=LocalFilesRepository):
        self.jobsDBRepository = jobs_db_repo()
        self.localFilesRepository = local_files_repo()

    def get_jobs(self) -> List[Job]:
        return self.jobsDBRepository.get_jobs()

    def get_job(self, job_id: int) -> Job:
        return self.jobsDBRepository.get_job(job_id)

    def create_job(self, job_data: Dict, upscale_params: Dict[str, Any], user: Any) -> Job:
        return self.jobsDBRepository.create_job(job_data)

    def test_inference(self, job_data: Dict) -> Job:
        return run_inference_task()

    def process_controller(self, job_data: Dict) -> Job:
        jobs_volumes_path = job_data['title_path']

        if not os.path.exists(jobs_volumes_path):
            raise FileNotFoundError(f"Directory {jobs_volumes_path} does not exist")

        # scanning available volumes of the title
        jobs_volumes = self.localFilesRepository.scan(jobs_volumes_path)

        print(jobs_volumes)
