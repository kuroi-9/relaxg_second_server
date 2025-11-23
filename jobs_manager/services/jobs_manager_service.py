import os
from typing import Dict, List, Any
from jobs_manager.models import Job
from jobs_manager.repositories.jobs_db_repository import JobsDBRepository
from jobs_manager.repositories.local_files_repository import LocalFilesRepository
from library.repositories.books_db_repository import BooksDBRepository
from jobs_manager.tasks import run_job_worker_task, calculate_job_progress
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery.result import AsyncResult
from rg_server.celery import app as celery_app

class JobsManagerService:
    def __init__(self, jobs_db_repo=JobsDBRepository, local_files_repo=LocalFilesRepository, books_db_repo=BooksDBRepository):
        self.jobsDBRepository = jobs_db_repo()
        self.localFilesRepository = local_files_repo()
        self.booksDBRepository = books_db_repo()

    def get_jobs(self) -> List[Job]:
        return self.jobsDBRepository.get_jobs()

    def get_jobs_progress(self) -> bool:
        try:
            jobs = self.jobsDBRepository.get_jobs()
            for job in jobs:
                calculate_job_progress(job.title_name)
        except Exception as e:
            print(f"Error getting jobs progress: {e}")
        return True

    def get_job(self, job_id: int) -> Job:
        return self.jobsDBRepository.get_job(job_id)

    def create_job(self, job_data: Dict, upscale_params: Dict[str, Any] | None, user: Any) -> Job:
        return self.jobsDBRepository.create_job(job_data)

    def delete_job(self, job_id: int) -> bool:
        res = self.stop_job(job_id)
        if res == 200:
            return self.jobsDBRepository.delete_job(job_id)
        return False

    def test_inference(self, job_data: Dict) -> None:
        '''Only for testing purposes'''
        return run_job_worker_task()

    def get_job_status(self, job_id: int):
        job = self.get_job(job_id)
        task_id = job.last_task_id
        print(f"Getting status for task {task_id}")

        active_tasks = celery_app.control.inspect().active()
        for running_tasks in active_tasks.items():
            for task in running_tasks:
                if len(task) > 0 and "id" in task[0] and task[0]["id"] == task_id:
                    print(f"Task {task_id} is running")
                    return True

        print(f"Task {task_id} not running")
        return False

    def stop_job(self, job_id: int):
        job = self.get_job(job_id)
        task_id = job.last_task_id
        try:
            print(f"Canceling task {task_id}")
            AsyncResult(task_id).revoke(terminate=True)
        except Exception as e:
            print(f"Error canceling task {task_id}: {e}")
            return 500
        return 200

    def prepare_job_worker(self, job_data: Dict) -> bool:
        '''
        Verifies that a created job can be ran, and start the associated worker
        '''

        self.stop_job(job_data['id'])
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


        task_id = run_job_worker_task.delay(job_data)
        print(f"Starting task {task_id}")
        job_data['last_task_id'] = task_id
        try:
            self.jobsDBRepository.update_job(job_data)
        except Exception as e:
            print(f"Error updating job data: {e}")
            return False
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'process_group',
                {
                    'type': 'process.message',
                    'message': 'Job worker started: ' + str(job_data['title_name']),
                }
            )
        return True
