from jobs_manager.models import Job
from typing import List

class JobsDBRepository:
    def create_job(self, data: dict) -> Job:
        job = Job(**data)
        job.save()
        return job

    def get_job(self, job_id: int) -> Job:
        try:
            return Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            raise Job.DoesNotExist(f"Job with id {job_id} does not exist")

    def get_jobs(self) -> List[Job]:
        return Job.objects.all()

    def update_job(self, job: Job) -> Job:
        job.save()
        return job

    def delete_job(self, job_id: int) -> None:
        try:
            job = Job.objects.get(id=job_id)
            job.delete()
        except Job.DoesNotExist:
            raise Job.DoesNotExist(f"Job with id {job_id} does not exist")
