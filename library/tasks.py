from celery import shared_task
# Import du service de library_app
from library.services.book_catalog_service import BookCatalogService
# Import du repository local_file_repository
from library.repositories.local_file_repository import LocalFileRepository
# Import du repository user_profile_repository pour obtenir le répertoire par défaut
from library.repositories.user_profile_repository import UserProfileRepository
import logging

logger = logging.getLogger(__name__)

@shared_task
def initiate_library_scan_task(scan_directory_path: str | None, user_id: int):
    # Prototype: Asynchronous task to launch complete library scan.
    # Pre-conditions: 'scan_directory_path' and 'user_id' are provided.
    # Post-conditions:
    # - Triggers 'process_single_scanned_book_task' for each new/updated file found.
    # - Logs the start and end of the scan.
    # - Handles errors at the global scan level (e.g., inaccessible directory).
    # **Relations:** Called by `BookCatalogService.initiate_library_scan()`.
    #   Interacts with `LocalFileRepository.list_available_books()`.
    #   Calls `process_single_scanned_book_task.delay()` for each file.
    pass

@shared_task
def process_single_scanned_book_task(file_path: str, user_id: int):
    # Prototype: Asynchronous task to process a single book found during scan.
    # Pre-conditions: 'file_path' and 'user_id' are provided.
    # Post-conditions:
    # - Calls the service to create/update book metadata.
    # - Updates book status based on processing success or failure.
    # - Logs results for each book.
    # **Relations:** Called by `initiate_library_scan_task`.
    #   Calls `BookCatalogService.process_scanned_book()`.
    pass
