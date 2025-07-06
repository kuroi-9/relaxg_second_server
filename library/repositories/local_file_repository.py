import os
from typing import List

class LocalFileRepository:
    # Prototype: Lists file paths with certain extensions in a given directory (recursive).
    # Pre-conditions: 'book_directory_path' is a valid path, 'extensions' is a list of formats (e.g., ['.cbz']).
    # Post-conditions: Returns a list of absolute file paths. Raises FileNotFoundError if the directory doesn't exist.
    def list_available_books(self, book_directory_path: str, extensions: List[str]) -> List[str]:
        available_books = []
        try:
            for dir in os.listdir(book_directory_path):
                # Walking in the book directory to scan volumes and their extension
                for root, dirs, files in os.walk(os.path.join(book_directory_path, dir)):
                    for file in files:
                        if file.endswith(tuple(extensions)):
                            available_books.append(os.path.join(root) + "/")
        except FileNotFoundError:
            raise FileNotFoundError(f"The directory '{book_directory_path}' does not exist.")
        return available_books

    # Prototype: Checks the existence and read accessibility of a file.
    # Pre-conditions: 'file_path' is a file path.
    # Post-conditions: Returns True if the file exists and is readable, False otherwise.
    def file_exists(self, file_path: str) -> bool:
        pass

    # Prototype: Gets the size of a file in bytes.
    # Pre-conditions: 'file_path' is the path of the file.
    # Post-conditions: Returns an integer representing the file size. Raises FileNotFoundError if the file does not exist.
    def get_file_size(self, file_path: str) -> int:
        pass
