from celery import shared_task

# Import du repository local_file_repository
from library.repositories.local_file_repository import LocalFileRepository

# Import du repository user_profile_repository pour obtenir le répertoire par défaut
# from library.repositories.user_profile_repository import UserProfileRepository
from library.repositories.book_db_repository import BookDBRepository
from library.services.single_scanned_volume_service import SingleScannedVolumeService
import logging
# from django.conf import settings

logger = logging.getLogger(__name__)
localFileRepository = LocalFileRepository()
bookDBRepository = BookDBRepository()
singleScannedVolumeService = SingleScannedVolumeService()


@shared_task
def initiate_library_scan_task(scan_books_directory_path: str | None, user_id: int):
    """
    Prototype: Asynchronous task to launch complete library scan.
    Pre-conditions: 'scan_directory_path' and 'user_id' are provided.
    Post-conditions:
    - Triggers 'process_single_scanned_series_task' for each new/updated file found.
    - Logs the start and end of the scan.
    - Handles errors at the global scan level (e.g., inaccessible directory).
    **Relations:** Called by `BookCatalogService.initiate_library_scan()`.
      Interacts with `LocalFileRepository.list_available_bookseries()`.
      Calls `process_single_scanned_series_task()` for each file.
    """

    # TODO: Get books dir from user profile
    # books_default_directory = getattr(settings, 'BOOKS_DIR')
    # if scan_books_directory_path is None:
    #     scan_books_directory_path = books_default_directory
    #
    # WIP: Setting moved in .env
    scan_books_directory_path = "/books/"

    assert scan_books_directory_path is not None
    available_bookseries_paths = localFileRepository.list_available_bookseries(
        scan_books_directory_path, [".cbz"]
    )
    for single_series_path in available_bookseries_paths:
        try:
            process_single_scanned_bookseries_task(single_series_path, user_id)
        except Exception as e:
            logger.error(f"Error processing book series {single_series_path}: {e}")

    logger.info("Library scan completed")
    return True


@shared_task
def process_single_scanned_bookseries_task(
    parent_bookseries_directory: str, user_id: int
):
    """
    Prototype: Asynchronous task to process a single book series found during scan.
    Pre-conditions: 'parent_series_directory' and 'user_id' are provided.
    Post-conditions:
    - Calls the service to process books metadata.
    - Updates book status based on processing success or failure. TODO: Find another way to handle errors
    - Logs results for each book.
    **Relations:** Called by `initiate_library_scan_task`.
      Calls `BookCatalogService.process_scanned_book()`.
    """

    volumes = localFileRepository.list_available_volumes(
        parent_bookseries_directory, [".cbz"]
    )
    for volume in volumes:
        isVolumeScannedSuccessfully = (
            singleScannedVolumeService.process_single_scanned_volume(
                volume, user_id, parent_bookseries_directory
            )
        )
        if isVolumeScannedSuccessfully:
            logger.info(
                f"Volume '{volume}' of '{parent_bookseries_directory}' scanned successfully."
            )
        else:
            logger.error(
                f"Failed to scan volume '{volume}' of '{parent_bookseries_directory}'."
            )

    logger.info(f"Scan completed for series '{parent_bookseries_directory}'")
