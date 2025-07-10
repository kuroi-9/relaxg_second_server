from celery import shared_task
# Import du repository local_file_repository
from library.repositories.local_file_repository import LocalFileRepository
# Import du repository user_profile_repository pour obtenir le répertoire par défaut
from library.repositories.user_profile_repository import UserProfileRepository
from library.services.book_catalog_service import BookDBRepository
import logging
from django.conf import settings


logger = logging.getLogger(__name__)
localFileRepository = LocalFileRepository()
bookDBRepository = BookDBRepository()

@shared_task
def initiate_library_scan_task(scan_books_directory_path: str | None, user_id: int):
    # Prototype: Asynchronous task to launch complete library scan.
    # Pre-conditions: 'scan_directory_path' and 'user_id' are provided.
    # Post-conditions:
    # - Triggers 'process_single_scanned_series_task' for each new/updated file found.
    # - Logs the start and end of the scan.
    # - Handles errors at the global scan level (e.g., inaccessible directory).
    # **Relations:** Called by `BookCatalogService.initiate_library_scan()`.
    #   Interacts with `LocalFileRepository.list_available_bookseries()`.
    #   Calls `process_single_scanned_series_task()` for each file.

    # TODO: Get books dir from user profile
    books_default_directory = getattr(settings, 'BOOKS_DIR')
    if scan_books_directory_path is None:
        scan_books_directory_path = books_default_directory

    assert scan_books_directory_path is not None
    available_bookseries_paths = localFileRepository.list_available_bookseries(scan_books_directory_path, [".cbz"])
    for single_series_path in available_bookseries_paths:
        process_single_scanned_bookseries_task(single_series_path, user_id)

    logger.info("Library scan completed")

@shared_task
def process_single_scanned_bookseries_task(parent_bookseries_directory: str, user_id: int):
    # Prototype: Asynchronous task to process a single book series found during scan.
    # Pre-conditions: 'parent_series_directory' and 'user_id' are provided.
    # Post-conditions:
    # - Calls the service to process books metadata.
    # - Updates book status based on processing success or failure. TODO: Find another way to handle errors
    # - Logs results for each book.
    # **Relations:** Called by `initiate_library_scan_task`.
    #   Calls `BookCatalogService.process_scanned_book()`.
    volumes = localFileRepository.list_available_volumes(parent_bookseries_directory, [".cbz"])
    for volume in volumes:
        isVolumeScannedSuccessfully = process_scanned_volume(volume, user_id, parent_bookseries_directory)
        if isVolumeScannedSuccessfully:
            logger.info(f"Volume '{volume}' of '{parent_bookseries_directory}' scanned successfully.")
        else:
            logger.error(f"Failed to scan volume '{volume}' of '{parent_bookseries_directory}'.")

    logger.info(f"Scan completed for series '{parent_bookseries_directory}'")

def process_scanned_volume(file_path: str, user_id: int, parent_bookseries_directory: str) -> bool:
    bookSeries = bookDBRepository.get_bookseries_by_filepath(parent_bookseries_directory)
    if bookSeries is None:
        try:
            bookDBRepository.create_bookseries({
                "directory_path": parent_bookseries_directory,
                "title": parent_bookseries_directory,
            })
        except Exception as e:
            raise Exception(f"Failed to create book series {parent_bookseries_directory}: {e}")

    # Checking if the book exists
    volume = bookDBRepository.get_volume_by_file_path(file_path)
    if volume is None:
        try:
            bookDBRepository.create_book({
                "file_path": file_path,
                "series": bookSeries,
            })
        except Exception as e:
            raise Exception(f"Failed to create book {file_path}: {e}")

    else:
        try:
            bookDBRepository.update_book(volume, { # Book ID will be checked in the repository
                "file_path": file_path,
                "series": bookSeries,
            })
        except Exception as e:
            raise Exception(f"Failed to update book {file_path}: {e}")

    # If no exception raised, return True
    return True;
