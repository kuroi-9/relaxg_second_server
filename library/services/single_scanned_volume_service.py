from library.repositories.local_file_repository import LocalFileRepository
from library.repositories.book_db_repository import BookDBRepository

class SingleScannedVolumeService:
    def __init__(self, local_file_repo=LocalFileRepository, book_db_repo=BookDBRepository):
        self.local_file_repository = local_file_repo()
        self.book_db_repository = book_db_repo()

    def process_single_scanned_volume(self, file_path: str, user_id: int, parent_bookseries_directory: str) -> bool:
        """Process a scanned volume.

        Args:
            file_path (str): The file path of the scanned volume.
            user_id (int): The ID of the user who initiated the scan.
            parent_bookseries_directory (str): The directory path of the parent book series.

        Returns:
            bool: True if the volume was scanned successfully, False otherwise.
        """

        bookSeries = self.book_db_repository.get_bookseries_by_filepath(parent_bookseries_directory)
        if bookSeries is None:
            try:
                self.book_db_repository.create_bookseries({
                    "directory_path": parent_bookseries_directory,
                    "title": parent_bookseries_directory,
                })
            except Exception as e:
                raise Exception(f"Failed to create book series {parent_bookseries_directory}: {e}")

        # Checking if the book exists
        volume = self.book_db_repository.get_volume_by_file_path(file_path)
        if volume is None:
            try:
                self.book_db_repository.create_book({
                    "file_path": file_path,
                    "series": bookSeries,
                })
            except Exception as e:
                raise Exception(f"Failed to create book {file_path}: {e}")

        else:
            try:
                self.book_db_repository.update_book(volume, { # Book ID will be checked in the repository
                    "file_path": file_path,
                    "series": bookSeries,
                })
            except Exception as e:
                raise Exception(f"Failed to update book {file_path}: {e}")

        # If no exception raised, return True
        return True;
