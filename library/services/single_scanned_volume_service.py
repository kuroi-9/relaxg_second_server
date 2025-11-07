from library.repositories.local_files_repository import LocalFilesRepository
from library.repositories.books_db_repository import BooksDBRepository


class SingleScannedVolumeService:
    def __init__(
        self, local_files_repo=LocalFilesRepository, books_db_repo=BooksDBRepository
    ):
        self.local_files_repository = local_files_repo()
        self.books_db_repository = books_db_repo()

    def process_single_scanned_volume(
        self, file_path: str, user_id: int, parent_bookseries_directory: str
    ) -> bool:
        """Process a scanned volume.

        Args:
            file_path (str): The file path of the scanned volume.
            user_id (int): The ID of the user who initiated the scan.
            parent_bookseries_directory (str): The directory path of the parent book series.

        Returns:
            bool: True if the volume was scanned successfully, False otherwise.
        """

        bookSeries = self.books_db_repository.get_bookseries_by_filepath(
            parent_bookseries_directory
        )
        if bookSeries is None:
            try:
                self.books_db_repository.create_bookseries(
                    {
                        "directory_path": parent_bookseries_directory,
                        "title": parent_bookseries_directory.split("/")[-2],
                        "cover_image": "/covers/" + parent_bookseries_directory.split("/")[-2].replace(" ", "_") + "_cover.jpg"
                    }
                )
            except Exception as e:
                raise Exception(
                    f"Failed to create bookseries {parent_bookseries_directory}: {e}"
                )


        bookSeries = self.books_db_repository.get_bookseries_by_filepath(
            parent_bookseries_directory
        )
        if bookSeries is None:
            raise Exception(
                f"Failed to find bookseries {parent_bookseries_directory}"
            )
        else:
            # Checking if the book exists
            volume = self.books_db_repository.get_volume_by_file_path(file_path)
            if volume is None:
                try:
                    self.books_db_repository.create_book(
                        {
                            "file_path": file_path,
                            "series": bookSeries,
                            "title": file_path.split("/")[-1].rsplit(".", 1)[0],
                            "status": "none"
                        }
                    )
                except Exception as e:
                    raise Exception(f"Failed to create book {file_path}: {e}")

            else:
                try:
                    self.books_db_repository.update_book(
                        volume,
                        {  # Book ID will be checked in the repository
                            "file_path": file_path,
                            "series": bookSeries,
                        },
                    )
                except Exception as e:
                    raise Exception(f"Failed to update book {file_path}: {e}")

            # If no exception raised, return True
        return True
