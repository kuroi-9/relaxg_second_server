from typing import Dict, List
from jobs_manager.models import Job
from jobs_manager.repositories.jobs_db_repository import JobsDBRepository
from jobs_manager.tasks import run_inference_task

class JobsManagerService:
    def __init__(self, jobs_db_repo=JobsDBRepository):
        self.jobsDBRepository = jobs_db_repo()

    def get_jobs(self) -> List[Job]:
        return self.jobsDBRepository.get_jobs()

    def create_job(self, job_data: Dict) -> Job:
        return self.jobsDBRepository.create_job(job_data)

    def test_inference(self, job_data: Dict) -> Job:
        return run_inference_task()
