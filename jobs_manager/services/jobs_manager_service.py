from typing import Dict, List
from jobs_manager.models import Job
from jobs_manager.repositories.jobs_db_repository import JobsDBRepository

class JobsManagerService:
    def __init__(self, jobs_db_repo=JobsDBRepository):
        self.jobsDBRepository = jobs_db_repo()

    def get_jobs(self) -> List[Job]:
        return self.jobsDBRepository.get_jobs()
