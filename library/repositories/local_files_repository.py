import os
from typing import List

class LocalFilesRepository:
    '''LocalFilesRepository class provides methods to interact with local files.'''

    def list_available_titles(self, titles_directory_path: str, extensions: List[str]) -> List[str]:
        '''
        Prototype: Lists titles paths with certain extensions in a given directory (recursive).
        Pre-conditions: 'titles_directory_path' is a valid path, 'extensions' is a list of formats (e.g., ['.cbz']).
        Post-conditions: Returns a list of absolute file paths. Raises FileNotFoundError if the directory doesn't exist
        '''

        available_titles = set()
        try:
            for dir in os.listdir(titles_directory_path):
                # Walking in the book directory to scan volumes and their extension
                for root, dirs, files in os.walk(os.path.join(titles_directory_path, dir)):
                    for file in files:
                        if file.endswith(tuple(extensions)):
                            split_path = os.path.split(root)
                            if split_path[1] != "out" and split_path[1] != "masked":
                                available_titles.add(os.path.join(root) + "/")
        except FileNotFoundError:
            raise FileNotFoundError(f"The directory '{titles_directory_path}' does not exist.")
        return list(available_titles)

    def list_available_books(self, parent_title_directory_path: str, extensions: List[str]) -> List[str]:
        '''Lists all available books in a given directory.'''

        available_books = []
        try:
            for root, dirs, files in os.walk(parent_title_directory_path):
                for file in files:
                    if file.endswith(tuple(extensions)):
                        split_path = os.path.split(root)
                        if split_path[1] != "out" and split_path[1] != "masked":
                            available_books.append(os.path.join(root, file))
        except FileNotFoundError:
            raise FileNotFoundError(f"The directory '{parent_title_directory_path}' does not exist.")
        return available_books


    def file_exists(self, file_path: str) -> bool:
        '''
        Prototype: Checks the existence and read accessibility of a file.
        Pre-conditions: 'file_path' is a file path.
        Post-conditions: Returns True if the file exists and is readable, False otherwise. Means to be used from other files.
        '''

        try:
            os.stat(file_path)
            return True
        except FileNotFoundError:
            return False


    def get_file_size(self, file_path: str) -> int:
        '''
        Prototype: Gets the size of a file in bytes.
        Pre-conditions: 'file_path' is the path of the file.
        Post-conditions: Returns an integer representing the file size. Raises FileNotFoundError if the file does not exist.
        '''

        try:
            return os.path.getsize(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
