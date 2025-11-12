from celery import shared_task
from django.conf import settings
from library.repositories.local_files_repository import LocalFilesRepository
# from library.repositories.user_profile_repository import UserProfileRepository
from library.repositories.books_db_repository import BooksDBRepository
from library.services.single_scanned_book_service import SingleScannedBookService
import logging

logger = logging.getLogger(__name__)
localFilesRepository = LocalFilesRepository()
booksDBRepository = BooksDBRepository()
singleScannedBookService = SingleScannedBookService()

@shared_task
def initiate_library_scan_task(scan_directory_path: str | None, user_id: int):
    """
    Prototype: Asynchronous task to launch complete library scan.
    Pre-conditions: 'scan_directory_path' and 'user_id' are provided.
    Post-conditions:
    - Triggers 'process_single_scanned_title_task' for each new/updated file found.
    - Logs the start and end of the scan.
    - Handles errors at the global scan level (e.g., inaccessible directory).
    **Relations:** Called by `BooksCatalogService.initiate_library_scan()`.
      Interacts with `localFilesRepository.list_available_titles()`.
      Calls `process_single_scanned_title_task()` for each file.
    """

    # TODO: Get books dir from user profile
    # books_default_directory = getattr(settings, 'BOOKS_DIR')
    # if scan_books_directory_path is None:
    #     scan_books_directory_path = books_default_directory
    #
    # WIP: Setting moved in .env
    scan_directory_path = scan_directory_path if scan_directory_path is not None else "/books/"

    assert scan_directory_path is not None
    available_titles_paths = localFilesRepository.list_available_titles(
        scan_directory_path, [".cbz"]
    )
    for single_title_path in available_titles_paths:
        try:
            process_single_scanned_title_task(single_title_path, user_id)
        except Exception as e:
            logger.error(f"Error processing title {single_title_path}: {e}")

    logger.info("Library scan completed")
    return True

@shared_task
def process_single_scanned_title_task(
    parent_title_directory: str, user_id: int
):
    """
    Prototype: Asynchronous task to process a single title found during scan.
    Pre-conditions: 'parent_title_directory' and 'user_id' are provided.
    Post-conditions:
    - Calls the service to process books metadata.
    - Updates book status based on processing success or failure. TODO: Find another way to handle errors
    - Logs results for each book.
    **Relations:** Called by `initiate_library_scan_task`.
      Calls `BooksCatalogService.process_single_scanned_book()`.
    """

    volumes = localFilesRepository.list_available_books(
        parent_title_directory, [".cbz"]
    )
    for volume in volumes:
        isVolumeScannedSuccessfully = (
            singleScannedBookService.process_single_scanned_book(
                volume, user_id, parent_title_directory
            )
        )
        if isVolumeScannedSuccessfully:
            logger.info(
                f"Volume '{volume}' of '{parent_title_directory}' scanned successfully."
            )
        else:
            logger.error(
                f"Failed to scan volume '{volume}' of '{parent_title_directory}'."
            )

    logger.info(f"Scan completed for title '{parent_title_directory}'")
