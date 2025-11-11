from jobs_manager.models import Job
from typing import List
from django.core.exceptions import ObjectDoesNotExist

class JobsDBRepository:
    def create_job(self, data: dict) -> Job:
        job = Job(**data)
        job.save()
        return job

    def get_job(self, job_id: int) -> Job:
        try:
            return Job._default_manager.get(id=job_id)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Job with id {job_id} does not exist")

    def get_jobs(self) -> List[Job]:
        return Job._default_manager.all()

    def update_job(self, job: Job) -> Job:
        job.save()
        return job

    def delete_job(self, job_id: int) -> None:
        try:
            job = Job._default_manager.get(id=job_id)
            job.delete()
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Job with id {job_id} does not exist")
