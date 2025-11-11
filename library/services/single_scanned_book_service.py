from library.repositories.local_files_repository import LocalFilesRepository
from library.repositories.books_db_repository import BooksDBRepository


class SingleScannedBookService:
    def __init__(
        self, local_files_repo=LocalFilesRepository, books_db_repo=BooksDBRepository
    ):
        self.local_files_repository = local_files_repo()
        self.books_db_repository = books_db_repo()

    def process_single_scanned_book(
        self, file_path: str, user_id: int, parent_title_directory: str
    ) -> bool:
        """Process a scanned book.

        Args:
            file_path (str): The file path of the scanned book.
            user_id (int): The ID of the user who initiated the scan.
            parent_title_directory (str): The directory path of the parent title.

        Returns:
            bool: True if the book was scanned successfully, False otherwise.
        """

        title = self.books_db_repository.get_title_by_filepath(
            parent_title_directory
        )
        if title is None:
            try:
                self.books_db_repository.create_title(
                    {
                        "directory_path": parent_title_directory,
                        "name": parent_title_directory.split("/")[-2],
                        "cover_image": "/covers/" + parent_title_directory.split("/")[-2].replace(" ", "_") + "_cover.jpg"
                    }
                )
            except Exception as e:
                raise Exception(
                    f"Failed to create title {parent_title_directory}: {e}"
                )


        title = self.books_db_repository.get_title_by_filepath(
            parent_title_directory
        )
        if title is None:
            raise Exception(
                f"Failed to find title {parent_title_directory}"
            )
        else:
            # Checking if the book exists
            volume = self.books_db_repository.get_book_by_file_path(file_path)
            if volume is None:
                try:
                    self.books_db_repository.create_book(
                        {
                            "file_path": file_path,
                            "name": file_path.split("/")[-1].rsplit(".", 1)[0],
                            "title": title,
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
                            "title": title,
                        },
                    )
                except Exception as e:
                    raise Exception(f"Failed to update book {file_path}: {e}")

            # If no exception raised, return True
        return True
