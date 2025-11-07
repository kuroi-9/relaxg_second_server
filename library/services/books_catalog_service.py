from typing import Dict, Any, List
from library.models import Book, BookSeries
from library.repositories.books_db_repository import BooksDBRepository
from library.repositories.local_files_repository import LocalFilesRepository
# Import service from other application for communication
#from upscale_processor_app.services.upscaling_orchestrator_service import UpscalingOrchestratorService
from library.tasks import initiate_library_scan_task

class BooksCatalogService:
    '''
    Orchestrator service for book catalog operations.
    This service manages the lifecycle of books in the library, including scanning, indexing, and retrieval.
    It also integrates with other services for advanced operations like upscaling images.
    '''

    def __init__(self, book_db_repo=BooksDBRepository, local_files_repo=LocalFilesRepository, upscale_service=None):
        self.booksDBRepository = book_db_repo()
        self.localFilesRepository = local_files_repo()

    def get_dashboard_books(self, user_id: int | None, filters: Dict[str, Any], pagination_params: Dict[str, Any]) -> List[BookSeries | None]:
        '''
        Prototype: Retrieve the list of books for the dashboard, with sorting and search options.
        Pre-conditions:
        - 'user_id' is the ID of the user requesting the list.
        - 'filters' is a dictionary of search/sort criteria.
        - 'pagination_params' contains 'page' and 'page_size'.
        Post-conditions:
        - Returns a paginated and sorted list of Book objects.
        - Raises ValueError if sort/search parameters are invalid.
        '''

        try:
            bookseries = self.booksDBRepository.get_bookseries_with_filters_and_order(filters, '-title')
            #TODO: Implement pagination logic
            return bookseries
        except ValueError as e:
            raise ValueError(f"Invalid sort/search parameters: {e}")

    def get_books_by_bookseries_title(self, bookseries_title: str) -> List[Book]:
        '''
        Retrieves all books associated with a book series from the database.
        Pre-conditions: 'bookseries_title' is the title of the book series.
        Post-conditions: Returns a list of Book instances.
        **Relations:** Calls `get_bookseries_books()`.

        '''

        try:
            return self.booksDBRepository.get_bookseries_books(bookseries_title)
        except ValueError as e:
            raise ValueError(f"Invalid book series title: {e}")

    def initiate_library_scan(self, scan_books_directory_path: str | None, user_id: int) -> bool:
        '''
        Prototype: Trigger analysis and update of the book database.
        Pre-conditions:
        - 'scan_directory_path' is the path of the directory to scan or None (for default).
        - 'user_id' is the ID of the user who triggered the scan.
        Post-conditions:
        - Returns True if the scan process is launched successfully (delegation to a Celery task).
        - Raises an Exception (e.g., PermissionError) if the directory is not accessible.
        **Relations:** Calls `initiate_library_scan_task.delay()`.
        '''

        return initiate_library_scan_task(scan_books_directory_path, user_id)

    # Prototype: Trigger an upscaling job via the 'upscale_processor_app' application service.
    # Pre-conditions:
    # - 'book_id' is the ID of the book to upscale (from `library_app.models.Book`).
    # - 'upscale_params' is a dictionary containing job parameters (e.g., 'preset_name').
    # - 'user' is the user object requesting the upscale.
    # Post-conditions:
    # - Returns the ID of the upscaling job created in the `upscale_processor_app` application.
    # - Raises ValueError if the book doesn't exist or if upscaling parameters are invalid.
    # - Raises Exception if communication with the upscaling service fails.
    # **Relations:** Interacts with `BooksDBRepository` (get_book_by_id) to obtain the file path.
    #   Calls `UpscalingOrchestratorService.create_upscale_job()` from the other application.
    def request_book_upscale(self, book_id: int, upscale_params: Dict[str, Any], user: Any) -> int:
        return 1 #TODO: Implement upscale job creation (including django app)

    def get_book_details(self, book_id: int) -> Book | None:
        '''
        Prototype: Retrieve the details of a specific book.
        Pre-conditions: 'book_id' is the ID of the book.
        Post-conditions: Returns the Book object or None.
        **Relations:** Interacts with `BooksDBRepository.get_book_by_id()`.
        '''

        book = self.booksDBRepository.get_book_by_id(book_id)
        if not book:
            raise ValueError(f"Book with ID {book_id} not found.")
        return book
