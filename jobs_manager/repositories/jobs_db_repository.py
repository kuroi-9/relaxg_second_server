from jobs_manager.models import Job
from typing import List
from django.core.exceptions import ObjectDoesNotExist

class JobsDBRepository:
    '''Repository for managing jobs in the database.'''
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
        return Job._default_manager.all().order_by('id')

    def update_job(self, job: dict) -> Job:
        job_instance = Job._default_manager.get(id=job['id'])
        job_instance.status = job.get('status', job_instance.status)
        job_instance.last_task_id = job.get('last_task_id', job_instance.last_task_id)
        job_instance.save()
        return job_instance

    def delete_job(self, job_id: int) -> bool:
        try:
            job = Job._default_manager.get(id=job_id)
            job.delete()
            return True
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(f"Job with id {job_id} does not exist")
