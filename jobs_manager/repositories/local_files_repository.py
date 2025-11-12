import os
from typing import List

class LocalFilesRepository:

    def __init__(self):
        pass

    def scan(self, books_dir: str) -> List[str]:
        '''
        Scans the /books/ directory for .cbz files and returns a list of their full paths.
        '''
        cbz_files: List[str] = []

        if not os.path.exists(books_dir):
            return cbz_files  # Return empty list if /books/ doesn't exist

        for root, _, files in os.walk(books_dir):
            for file in files:
                if file.endswith(".cbz"):
                    cbz_files.append(os.path.join(root, file))

        cbz_files.sort()
        return cbz_files

    def extraction(self, title_dir: str, cbz_file: str):
        '''
        Prototype: Extracts the contents of a .cbz file located in the specified title directory.
        Pre-conditions:
        - 'title_dir' is the name of the title directory inside '/books/'
        - 'cbz_file' is the name of the .cbz file.
        Post-conditions: Extracts the .cbz file into the title directory. Raises FileNotFoundError if the file or directory does not exist.
        '''

        out_path = '/out/'
        cbz_path = cbz_file

        if not os.path.exists(out_path):
            raise FileNotFoundError(f"The directory '{out_path}' does not exist.")

        if not os.path.isfile(cbz_path):
            raise FileNotFoundError(f"The file '{cbz_path}' does not exist.")

        # Ensure the extraction directory exists
        extraction_dir = os.path.join(out_path, title_dir, cbz_file.split("/")[-1].rsplit(".", 1)[0])
        os.makedirs(extraction_dir, exist_ok=True)

        # Extract the .cbz file (assuming it's a zip archive)
        import zipfile
        with zipfile.ZipFile(cbz_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_dir)

    def resizing(self):
        pass

    def finalization(self):
        pass
