from django.test import TestCase
from unittest.mock import patch
from library.repositories.local_files_repository import localFilesRepository

class localFilesRepositoryTests(TestCase):
    def setUp(self):
        # Préparer une instance du repository pour chaque test
        self.repository = localFilesRepository()

    # =============================================================================
    # Tests for list_available_book_series() method
    # =============================================================================

    def test_list_available_book_series_basic_structure(self):
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
                return [('/mock/root/dir1', ['out', 'masked'], ['file3.cbz', 'file4.txt'])]
            elif path == '/mock/root/dir2':
                return [('/mock/root/dir2', [], ['file5.cbz'])]
            elif path == '/mock/root/dir1/out':
                return [('/mock/root/dir1/out', [], ['file6.cbz', 'file7.txt'])]
            elif path == '/mock/root/dir1/masked':
                return [('/mock/root/dir1/masked', [], ['file8.cbz', 'file9.txt'])]
            return []

        expected_files = [
            '/mock/root/dir1/',
            '/mock/root/dir2/',
        ]
        extensions = ['.cbz']

        # Use of patch to replace the real functions of 'os'
        with patch('os.listdir', return_value=mock_listdir_return_value), \
             patch('os.walk', side_effect=mock_os_walk_side_effect):
            # Call the function to test
            actual_files = self.repository.list_available_bookseries('/mock/root', extensions)

            # Verify assertions
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))


    def test_list_available_book_series_empty_directory(self):
        # Prototype: Tests the scenario with an empty directory.
        # Pre-conditions:
        # - A mock of 'os.listdir' is configured to return an empty list.
        # Post-conditions:
        # - The function should return an empty list.
        # Relations: Calls `os.listdir` (mocked).

        mock_listdir_return_value = []
        extensions = ['.cbz']

        with patch('os.listdir', return_value=mock_listdir_return_value):
            actual_files = self.repository.list_available_bookseries('/mock/root', extensions)
            self.assertEqual(actual_files, [])
            self.assertEqual(len(actual_files), 0)

    def test_list_available_book_series_no_matching_extensions(self):
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
            actual_files = self.repository.list_available_bookseries('/mock/root', extensions)
            self.assertEqual(actual_files, [])
            self.assertEqual(len(actual_files), 0)

    def test_list_available_book_series_invalid_path(self):
        # Prototype: Tests the scenario where the starting path is invalid/does not exist.
        # Pre-conditions:
        # - A mock of 'os.listdir' is configured to raise a FileNotFoundError.
        # Post-conditions:
        # - The function should propagate the FileNotFoundError according to the implementation.
        # Relations: Calls `os.listdir` (mocked).

        extensions = ['.cbz']

        with patch('os.listdir', side_effect=FileNotFoundError("Directory not found")):
            with self.assertRaises(FileNotFoundError) as context:
                self.repository.list_available_bookseries('/invalid/path', extensions)

            self.assertIn("The directory '/invalid/path' does not exist.", str(context.exception))

    def test_list_available_book_series_with_special_characters(self):
        # Prototype: Tests the scenario with directories containing special characters.
        # Pre-conditions:
        # - A mock of 'os.listdir' and 'os.walk' configured with directories having special characters.
        # Post-conditions:
        # - The function should return a list containing the paths of directories with special characters.
        # Relations: Calls `os.listdir` and `os.walk` (mocked).

        mock_listdir_return_value = ['dir with spaces', 'dir_éàç', 'dir[brackets]']

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/dir with spaces':
                return [('/mock/root/dir with spaces', [], ['volume1.cbz'])]
            elif path == '/mock/root/dir_éàç':
                return [('/mock/root/dir_éàç', [], ['volume2.cbz'])]
            elif path == '/mock/root/dir[brackets]':
                return [('/mock/root/dir[brackets]', [], ['volume3.cbz'])]
            return []

        expected_files = [
            '/mock/root/dir with spaces/',
            '/mock/root/dir_éàç/',
            '/mock/root/dir[brackets]/'
        ]
        extensions = ['.cbz']

        with patch('os.listdir', return_value=mock_listdir_return_value), \
             patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_bookseries('/mock/root', extensions)
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))

    def test_list_available_book_series_multiple_extensions(self):
        # Prototype: Tests the scenario with multiple accepted extensions.
        # Pre-conditions:
        # - A mock of 'os.listdir' and 'os.walk' configured with files of different extensions.
        # Post-conditions:
        # - The function should return a list containing directories that have files matching any of the extensions.
        # Relations: Calls `os.listdir` and `os.walk` (mocked).

        mock_listdir_return_value = ['series1', 'series2', 'series3']

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/series1':
                return [('/mock/root/series1', [], ['volume1.cbz'])]
            elif path == '/mock/root/series2':
                return [('/mock/root/series2', [], ['volume2.cbr'])]
            elif path == '/mock/root/series3':
                return [('/mock/root/series3', [], ['volume3.zip'])]
            return []

        expected_files = [
            '/mock/root/series1/',
            '/mock/root/series2/',
            '/mock/root/series3/'
        ]
        extensions = ['.cbz', '.cbr', '.zip']

        with patch('os.listdir', return_value=mock_listdir_return_value), \
             patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_bookseries('/mock/root', extensions)
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))

    def test_list_available_book_series_case_sensitive_extensions(self):
        # Prototype: Tests the scenario with extensions in upper/lower case.
        # Pre-conditions:
        # - A mock of 'os.listdir' and 'os.walk' configured with files having mixed case extensions.
        # Post-conditions:
        # - The function should respect the case of extensions (default behavior of endswith).
        # Relations: Calls `os.listdir` and `os.walk` (mocked).

        mock_listdir_return_value = ['series1', 'series2', 'series3']

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/series1':
                return [('/mock/root/series1', [], ['volume1.cbz'])]
            elif path == '/mock/root/series2':
                return [('/mock/root/series2', [], ['volume2.CBZ'])]
            elif path == '/mock/root/series3':
                return [('/mock/root/series3', [], ['volume3.Cbz'])]
            return []

        expected_files = [
            '/mock/root/series1/'
        ]
        extensions = ['.cbz']  # Only lowercase

        with patch('os.listdir', return_value=mock_listdir_return_value), \
             patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_bookseries('/mock/root', extensions)
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))

    def test_list_available_book_series_nested_directories(self):
        # Prototype: Tests the scenario with nested directories containing volumes.
        # Pre-conditions:
        # - A mock of 'os.listdir' and 'os.walk' configured with nested directory structures.
        # Post-conditions:
        # - The function should return unique directory paths containing matching files (no duplicates).
        # Relations: Calls `os.listdir` and `os.walk` (mocked).

        mock_listdir_return_value = ['manga_series']

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/manga_series':
                return [
                    ('/mock/root/manga_series', ['season1', 'season2'], []),
                    ('/mock/root/manga_series/season1', [], ['vol1.cbz', 'vol2.cbz']),
                    ('/mock/root/manga_series/season2', [], ['vol3.cbz'])
                ]
            return []

        expected_files = [
            '/mock/root/manga_series/season1/',
            '/mock/root/manga_series/season2/'
        ]
        extensions = ['.cbz']

        with patch('os.listdir', return_value=mock_listdir_return_value), \
             patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_bookseries('/mock/root', extensions)
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))

    def test_list_available_book_series_no_duplicates(self):
        # Prototype: Tests that no duplicate paths are returned when multiple files exist in the same directory.
        # Pre-conditions:
        # - A mock of 'os.listdir' and 'os.walk' configured with multiple files in the same directories.
        # Post-conditions:
        # - The function should return unique directory paths only (no duplicates).
        # Relations: Calls `os.listdir` and `os.walk` (mocked).

        mock_listdir_return_value = ['series1', 'series2']

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/series1':
                return [('/mock/root/series1', [], ['vol1.cbz', 'vol2.cbz', 'vol3.cbz', 'vol4.cbz'])]
            elif path == '/mock/root/series2':
                return [
                    ('/mock/root/series2', ['season1'], []),
                    ('/mock/root/series2/season1', [], ['vol1.cbz', 'vol2.cbz'])
                ]
            return []

        expected_files = [
            '/mock/root/series1/',
            '/mock/root/series2/season1/'
        ]
        extensions = ['.cbz']

        with patch('os.listdir', return_value=mock_listdir_return_value), \
             patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_bookseries('/mock/root', extensions)

            # Check that we have the expected unique paths
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))

            # Verify no duplicates by checking that converting to set doesn't change length
            self.assertEqual(len(actual_files), len(set(actual_files)))

    # =============================================================================
    # Tests for list_available_volumes() method
    # =============================================================================

    def test_list_available_volumes_basic_structure(self):
        # Prototype: Tests the basic scenario with some files and folders.
        # Pre-conditions:
        # - A mock of 'os.walk' is configured to simulate a directory structure with volumes.
        # Post-conditions:
        # - The function should return a list containing the absolute paths of individual volume files.
        # - No volume should be missing and no volume with unexpected extension should be present.
        # Relations: Calls `os.walk` which is mocked.

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/series':
                return [
                    ('/mock/root/series', ['title1', 'title2'], ['readme.txt']),
                    ('/mock/root/series/title1', ['out', 'masked'], ['volume1.cbz', 'volume2.cbz', 'info.txt']),
                    ('/mock/root/series/title1/out', [], ['volume1.cbz', 'volume2.cbz', 'info.txt']),
                    ('/mock/root/series/title1/masked', [], ['volume10.cbz']),
                    ('/mock/root/series/title2', [], ['volume3.cbr', 'volume4.cbz'])
                ]
            return []

        expected_files = [
            '/mock/root/series/title1/volume1.cbz',
            '/mock/root/series/title1/volume2.cbz',
            '/mock/root/series/title2/volume3.cbr',
            '/mock/root/series/title2/volume4.cbz'
        ]
        extensions = ['.cbz', '.cbr']

        # Use of patch to replace the real functions of 'os'
        with patch('os.walk', side_effect=mock_os_walk_side_effect):
            # Call the function to test
            actual_files = self.repository.list_available_volumes('/mock/root/series', extensions)

            # Verify assertions
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))

    def test_list_available_volumes_empty_directory(self):
        # Prototype: Tests the scenario with an empty directory.
        # Pre-conditions:
        # - A mock of 'os.walk' is configured to return a directory without files.
        # Post-conditions:
        # - The function should return an empty list.
        # Relations: Calls `os.walk` (mocked).

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/empty':
                return [('/mock/root/empty', [], [])]
            return []

        extensions = ['.cbz']

        with patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_volumes('/mock/root/empty', extensions)
            self.assertEqual(actual_files, [])
            self.assertEqual(len(actual_files), 0)

    def test_list_available_volumes_no_matching_extensions(self):
        # Prototype: Tests the scenario where no files match the given extensions.
        # Pre-conditions:
        # - A mock of 'os.walk' is configured with files, but no extension matches.
        # Post-conditions:
        # - The function should return an empty list.
        # Relations: Calls `os.walk` (mocked).

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/series':
                return [
                    ('/mock/root/series/', ['title1']),
                    ('/mock/root/series/title1', [], ['file1.txt', 'file2.pdf', 'file3.docx'])]
            return []

        extensions = ['.cbz']

        with patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_volumes('/mock/root/series/title1/', extensions)
            self.assertEqual(actual_files, [])
            self.assertEqual(len(actual_files), 0)

    def test_list_available_volumes_invalid_path(self):
        # Prototype: Tests the scenario where the starting path is invalid/does not exist.
        # Pre-conditions:
        # - A mock of 'os.walk' is configured to raise a FileNotFoundError.
        # Post-conditions:
        # - The function should propagate the FileNotFoundError according to the implementation.
        # Relations: Calls `os.walk` (mocked).

        extensions = ['.cbz']

        with patch('os.walk', side_effect=FileNotFoundError("Directory not found")):
            with self.assertRaises(FileNotFoundError) as context:
                self.repository.list_available_volumes('/invalid/path', extensions)

            self.assertIn("The directory '/invalid/path' does not exist.", str(context.exception))

    def test_list_available_volumes_with_special_characters(self):
        # Prototype: Tests the scenario with files containing special characters.
        # Pre-conditions:
        # - A mock of 'os.walk' is configured with files having special characters in names.
        # Post-conditions:
        # - The function should return a list containing the absolute paths of files with special characters.
        # Relations: Calls `os.walk` (mocked).

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/special':
                return [
                    ('/mock/root/special', ['dir with spaces', 'dir_éàç'], []),
                    ('/mock/root/special/dir with spaces', [], ['volume with spaces.cbz', 'volume-normal.cbz']),
                    ('/mock/root/special/dir_éàç', [], ['volume_éàç.cbz', 'volume[brackets].cbz'])
                ]
            return []

        expected_files = [
            '/mock/root/special/dir with spaces/volume with spaces.cbz',
            '/mock/root/special/dir with spaces/volume-normal.cbz',
            '/mock/root/special/dir_éàç/volume_éàç.cbz',
            '/mock/root/special/dir_éàç/volume[brackets].cbz'
        ]
        extensions = ['.cbz']

        with patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_volumes('/mock/root/special', extensions)
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))

    def test_list_available_volumes_multiple_extensions(self):
        # Prototype: Tests the scenario with multiple accepted extensions.
        # Pre-conditions:
        # - A mock of 'os.walk' is configured with files of different extensions.
        # Post-conditions:
        # - The function should return a list containing all files matching the extensions.
        # Relations: Calls `os.walk` (mocked).

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/mixed':
                return [('/mock/root/mixed', [], ['volume1.cbz', 'volume2.cbr', 'volume3.zip', 'volume4.txt'])]
            return []

        expected_files = [
            '/mock/root/mixed/volume1.cbz',
            '/mock/root/mixed/volume2.cbr',
            '/mock/root/mixed/volume3.zip'
        ]
        extensions = ['.cbz', '.cbr', '.zip']

        with patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_volumes('/mock/root/mixed', extensions)
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))

    def test_list_available_volumes_case_sensitive_extensions(self):
        # Prototype: Tests the scenario with extensions in upper/lower case.
        # Pre-conditions:
        # - A mock of 'os.walk' is configured with files having mixed case extensions.
        # Post-conditions:
        # - The function should respect the case of extensions (default behavior of endswith).
        # Relations: Calls `os.walk` (mocked).

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/case':
                return [('/mock/root/case', [], ['volume1.cbz', 'volume2.CBZ', 'volume3.Cbz'])]
            return []

        expected_files = [
            '/mock/root/case/volume1.cbz'
        ]
        extensions = ['.cbz']  # Only lowercase

        with patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_volumes('/mock/root/case', extensions)
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))

    def test_list_available_volumes_complex_directory_structure(self):
        # Prototype: Tests the scenario with a complex nested directory structure.
        # Pre-conditions:
        # - A mock of 'os.walk' is configured with multiple levels of nesting and mixed file types.
        # Post-conditions:
        # - The function should return a list containing all volume files from all nested directories.
        # Relations: Calls `os.walk` (mocked).

        def mock_os_walk_side_effect(path):
            if path == '/mock/root/library':
                return [
                    ('/mock/root/library', ['manga', 'comics'], ['catalog.txt']),
                    ('/mock/root/library/manga', ['series1', 'series2'], []),
                    ('/mock/root/library/manga/series1', ['season1', 'season2'], ['description.txt']),
                    ('/mock/root/library/manga/series1/season1', [], ['vol1.cbz', 'vol2.cbz', 'extras.pdf']),
                    ('/mock/root/library/manga/series1/season2', [], ['vol3.cbz']),
                    ('/mock/root/library/manga/series2', [], ['standalone.cbr']),
                    ('/mock/root/library/comics', ['dc', 'marvel'], []),
                    ('/mock/root/library/comics/dc', [], ['batman.cbz', 'superman.cbz']),
                    ('/mock/root/library/comics/marvel', [], ['spiderman.cbr', 'xmen.zip'])
                ]
            return []

        expected_files = [
            '/mock/root/library/manga/series1/season1/vol1.cbz',
            '/mock/root/library/manga/series1/season1/vol2.cbz',
            '/mock/root/library/manga/series1/season2/vol3.cbz',
            '/mock/root/library/manga/series2/standalone.cbr',
            '/mock/root/library/comics/dc/batman.cbz',
            '/mock/root/library/comics/dc/superman.cbz',
            '/mock/root/library/comics/marvel/spiderman.cbr',
            '/mock/root/library/comics/marvel/xmen.zip'
        ]
        extensions = ['.cbz', '.cbr', '.zip']

        with patch('os.walk', side_effect=mock_os_walk_side_effect):
            actual_files = self.repository.list_available_volumes('/mock/root/library', extensions)
            self.assertCountEqual(actual_files, expected_files)
            self.assertEqual(len(actual_files), len(expected_files))
