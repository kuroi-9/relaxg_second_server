from django.test import TestCase
from unittest.mock import patch
from library.repositories.local_file_repository import LocalFileRepository

class LocalFileRepositoryTests(TestCase):
    def setUp(self):
        # Préparer une instance du repository pour chaque test
        self.repository = LocalFileRepository()

    def test_list_available_books_basic_structure(self):
        # Prototype: Tests the basic scenario with some files and folders.
        # Pre-conditions:
        # - A mock of 'os.listdir' is configured to simulate subdirectories.
        # - A mock of 'os.walk' is configured to simulate a simple directory structure.
        # Post-conditions:
        # - The function should return a list containing the absolute paths of compatible book folders
        # - No folder should be missing and folder with unexpected file should not be present.
        # Relations: Calls `os.listdir` and `os.walk` which are mocked.

        mock_listdir_return_value = ['dir1', 'dir2']

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/dir1':
                return [('/mock/root/dir1', [], ['file3.cbz', 'file4.txt'])]
            elif path == '/mock/root/dir2':
                return [('/mock/root/dir2', [], ['file5.cbz'])]
            return []

        expected_files = [
            '/mock/root/dir1/',
            '/mock/root/dir2/'
        ]
        extensions = ['.cbz']

        # Use of patch to replace the real functions of 'os'
        with patch('os.listdir', return_value=mock_listdir_return_value), \
             patch('os.walk', side_effect=mock_os_walk_side_effect):
            # Call the function to test
            actual_files = self.repository.list_available_books('/mock/root', extensions)

            # Verify assertions
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))


    def test_list_available_books_empty_directory(self):
        # Prototype: Tests the scenario with an empty directory.
        # Pre-conditions:
        # - A mock of 'os.listdir' is configured to return an empty list.
        # Post-conditions:
        # - The function should return an empty list.
        # Relations: Calls `os.listdir` (mocked).

        mock_listdir_return_value = []
        extensions = ['.cbz']

        with patch('os.listdir', return_value=mock_listdir_return_value):
            actual_files = self.repository.list_available_books('/mock/root', extensions)
            self.assertEqual(actual_files, [])
            self.assertEqual(len(actual_files), 0)

    def test_list_available_books_no_matching_extensions(self):
        # Prototype: Tests the scenario where no book folder contains files matching the given extensions.
        # Pre-conditions:
        # - A mock of 'os.listdir' and 'os.walk' are configured with files, but no extension matches.
        # Post-conditions:
        # - The function should return an empty list.
        # Relations: Calls `os.listdir` and `os.walk` (mocked).

        mock_listdir_return_value = ['dir1']

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/dir1':
                return [('/mock/root/dir1', [], ['file1.txt', 'file2.pdf'])]
            return []

        extensions = ['.cbz']

        with patch('os.listdir', return_value=mock_listdir_return_value), \
             patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_books('/mock/root', extensions)
            self.assertEqual(actual_files, [])
            self.assertEqual(len(actual_files), 0)

    def test_list_available_books_invalid_path(self):
        # Prototype: Tests the scenario where the starting path is invalid/does not exist.
        # Pre-conditions:
        # - A mock of 'os.listdir' is configured to raise a FileNotFoundError.
        # Post-conditions:
        # - The function should propagate the FileNotFoundError according to the implementation.
        # Relations: Calls `os.listdir` (mocked).

        extensions = ['.cbz']

        with patch('os.listdir', side_effect=FileNotFoundError("Directory not found")):
            with self.assertRaises(FileNotFoundError) as context:
                self.repository.list_available_books('/invalid/path', extensions)

            self.assertIn("The directory '/invalid/path' does not exist.", str(context.exception))
