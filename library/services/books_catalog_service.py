from typing import Dict, Any, List
from library.models import Book, Title
from library.repositories.books_db_repository import BooksDBRepository
from library.repositories.local_files_repository import LocalFilesRepository
from library.tasks import initiate_library_scan_task
from jobs_manager.services.jobs_manager_service import JobsManagerService
from jobs_manager.models import Job

class BooksCatalogService:
    '''
    Orchestrator service for book catalog operations.
    This service manages the lifecycle of books in the library, including scanning, indexing, and retrieval.
    It also integrates with other services for upscaling operations.
    '''

    def __init__(self, book_db_repo=BooksDBRepository, local_files_repo=LocalFilesRepository, jobs_manager_service=JobsManagerService):
        self.booksDBRepository = book_db_repo()
        self.localFilesRepository = local_files_repo()
        self.jobsManagerService = jobs_manager_service()

    def get_dashboard_titles(self, user_id: int | None, filters: Dict[str, Any], pagination_params: Dict[str, Any]) -> List[Title | None]:
        '''
        Prototype: Retrieve the list of books for the dashboard, with sorting and search options.
        Pre-conditions:
        - 'user_id' is the ID of the user requesting the list.
        - 'filters' is a dictionary of search/sort criteria.
        - 'pagination_params' contains 'page' and 'page_size'.
        Post-conditions:
        - Returns a paginated and sorted list of Book instances.
        - Raises ValueError if sort/search parameters are invalid.
        '''

        try:
            titles = self.booksDBRepository.get_titles_with_filters_and_order(filters, '-name')
            #TODO: Implement pagination logic
            return titles
        except ValueError as e:
            raise ValueError(f"Invalid sort/search parameters: {e}")

    def get_books_by_title_name(self, title_name: str) -> List[Book]:
        '''
        Retrieves all books associated with a title from the database.
        Pre-conditions: 'title_name' is the title of the book.
        Post-conditions: Returns a list of Book instances.
        '''

        try:
            return self.booksDBRepository.get_title_books(title_name)
        except ValueError as e:
            raise ValueError(f"Invalid book title: {e}")

    def initiate_library_scan(self, scan_directory_path: str | None, user_id: int) -> bool:
        '''
        Prototype: Trigger analysis and update of the book database.
        Pre-conditions:
        - 'scan_directory_path' is the path of the directory to scan or None (for default).
        - 'user_id' is the ID of the user who triggered the scan.
        Post-conditions:
        - Returns True if the scan process is completed successfully.
        - Raises an Exception (e.g., PermissionError) if the directory is not accessible.
        '''

        res = initiate_library_scan_task.apply((scan_directory_path, user_id,),)
        return res.successful()


    def request_title_upscale(self, title_id: int, upscale_params: Dict[str, Any] | None, user: Any) -> Job:
        '''
        Prototype: Create an upscale job for a title.
        Pre-conditions:
        - 'title_id' is the ID of the title to upscale.
        - 'upscale_params' is a dictionary containing parameters for the upscale job.
        - 'user' is the user initiating the upscale request.
        Post-conditions:
        - Raises ValueError if the title is not found.
        '''

        title = self.booksDBRepository.get_title_by_id(title_id)
        if not title:
            raise ValueError(f"Title with ID {title_id} not found for upscaling.")

        job_data = {
            'title_name': title.name,
            'title_path': title.directory_path,
            'description': title.description,
            'images_number': 0, # Defaulting to 0, actual number will be determined during the scanning step
            'status': 'original', # Initial status for a new upscale job
            'step': 'scanning', # Starting with scanning to identify images
            'used_model_name': '4x-eula-digimanga-bw-v2-nc1',
            # 'created_at' is handled by the Job model's defaults
        }

        # The create_job method in JobManagerService is expected to accept a dictionary
        # containing the job's initial data and the user initiating the job.
        return self.jobsManagerService.create_job(job_data, upscale_params, user)

    def get_book_details(self, book_id: int) -> Book | None:
        '''
        Prototype: Retrieve the details of a specific book.
        Pre-conditions: 'book_id' is the ID of the book.
        Post-conditions: Returns the Book object or None.
        '''

        book = self.booksDBRepository.get_book_by_id(book_id)
        if not book:
            raise ValueError(f"Book with ID {book_id} not found.")
        return book
