import unittest
from unittest.mock import patch
from django.conf import settings
from library.tasks import (
    initiate_library_scan_task,
    process_single_scanned_title_task,
)

class TasksTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure minimal Django settings for tests
        if not settings.configured:
            settings.configure(
                BOOKS_DIR='/mock/books/dir',
                DEBUG=True,
                INSTALLED_APPS=[
                    'django.contrib.auth',
                    'django.contrib.contenttypes',
                    'library',
                ],
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': ':memory:',
                    }
                },
            )

    # Mocked functions and methods, reversed in the test prototype
    @patch('library.tasks.localFilesRepository')
    @patch('library.tasks.BooksDBRepository')
    @patch('library.tasks.singleScannedBookService')
    @patch('library.tasks.process_single_scanned_title_task') # Mock the celery task call
    def test_initiate_library_scan_task_with_default_path(self, mock_process_task, mock_single_scanned_book_service, mock_books_db_repository, mock_local_files_repository):
        """
        Test initiate_library_scan_task when scan_books_directory_path is None,
        using the default BOOKS_DIR from settings.
        """
        # Setup mocks
        mock_local_files_repository.list_available_titles.return_value = [
            '/mock/books/dir/series1',
            '/mock/books/dir/series2'
        ]

        # Call the task
        result = initiate_library_scan_task(None, 1)

        # Assertions
        mock_local_files_repository.list_available_titles.assert_called_once_with(
            '/books/', [".cbz"]
        )
        # Verify that process_single_scanned_titles_task was called for each series
        mock_process_task.assert_any_call('/mock/books/dir/series1', 1)
        mock_process_task.assert_any_call('/mock/books/dir/series2', 1)
        self.assertEqual(mock_process_task.call_count, 2)
        self.assertTrue(result)

    @patch('library.tasks.localFilesRepository')
    @patch('library.tasks.BooksDBRepository')
    @patch('library.tasks.singleScannedBookService')
    @patch('library.tasks.process_single_scanned_title_task')
    def test_initiate_library_scan_task_with_specific_path(self, mock_process_task, mock_single_scanned_book_service, mock_books_db_repository, mock_local_files_repository):
        """
        Test initiate_library_scan_task with a specific scan_books_directory_path.
        """
        mock_local_files_repository.list_available_titles.return_value = [
            '/custom/path/seriesA'
        ]
        custom_path = '/custom/path'

        result = initiate_library_scan_task(custom_path, 2)

        mock_local_files_repository.list_available_titles.assert_called_once_with(
            custom_path, [".cbz"]
        )
        mock_process_task.assert_called_once_with('/custom/path/seriesA', 2)
        self.assertTrue(result)

    @patch('library.tasks.localFilesRepository')
    @patch('library.tasks.BooksDBRepository')
    @patch('library.tasks.singleScannedBookService')
    def test_process_single_scanned_titles_task_success(self, mock_single_scanned_book_service, mock_books_db_repository, mock_local_files_repository):
        """
        Test process_single_scanned_titles_task when volume processing is successful.
        """
        mock_local_files_repository.list_available_books.return_value = [
            'volume1.cbz',
            'volume2.cbz'
        ]
        mock_single_scanned_book_service.process_single_scanned_book.return_value = True

        parent_dir = '/mock/books/dir/series1'
        user_id = 1

        process_single_scanned_title_task(parent_dir, user_id)

        mock_local_files_repository.list_available_books.assert_called_once_with(
            parent_dir, [".cbz"]
        )
        # Verify process_single_scanned_book was called for each volume
        mock_single_scanned_book_service.process_single_scanned_book.assert_any_call(
            'volume1.cbz', user_id, parent_dir
        )
        mock_single_scanned_book_service.process_single_scanned_book.assert_any_call(
            'volume2.cbz', user_id, parent_dir
        )
        self.assertEqual(mock_single_scanned_book_service.process_single_scanned_book.call_count, 2)

    @patch('library.tasks.localFilesRepository')
    @patch('library.tasks.BooksDBRepository')
    @patch('library.tasks.singleScannedBookService')
    def test_process_single_scanned_titles_task_failure(self, mock_single_scanned_book_service, mock_books_db_repository, mock_local_files_repository):
        """
        Test process_single_scanned_titles_task when some volume processing fails.
        """
        mock_local_files_repository.list_available_books.return_value = [
            'volume1.cbz',
            'volume2.cbz'
        ]
        # Make the first call succeed, the second fail
        mock_single_scanned_book_service.process_single_scanned_book.side_effect = [True, False]

        parent_dir = '/mock/books/dir/series2'
        user_id = 2

        # Mock the logger to check if error is logged
        with patch('library.tasks.logger') as mock_logger:
            process_single_scanned_title_task(parent_dir, user_id)

            mock_local_files_repository.list_available_books.assert_called_once_with(
                parent_dir, [".cbz"]
            )
            self.assertEqual(mock_single_scanned_book_service.process_single_scanned_book.call_count, 2)
            mock_logger.error.assert_called_once_with("Failed to scan volume 'volume2.cbz' of '/mock/books/dir/series2'.")

    @patch('library.tasks.localFilesRepository')
    @patch('library.tasks.BooksDBRepository')
    @patch('library.tasks.singleScannedBookService')
    @patch('library.tasks.process_single_scanned_title_task')
    def test_initiate_library_scan_task_with_error_in_processing_series(self, mock_process_task, mock_single_scanned_book_service, mock_books_db_repository, mock_local_files_repository):
        """
        Test initiate_library_scan_task when one of the series processing fails.
        """
        mock_local_files_repository.list_available_titles.return_value = [
            '/mock/books/dir/series1',
            '/mock/books/dir/series2'
        ]
        # Make the first call to process_single_scanned_titles_task succeed, the second fail
        mock_process_task.side_effect = [None, Exception("Simulated processing error")]

        parent_dir = None
        user_id = 1

        # Mock the logger to check if error is logged
        with patch('library.tasks.logger') as mock_logger:
            result = initiate_library_scan_task(parent_dir, user_id)

            mock_process_task.assert_any_call('/mock/books/dir/series1', 1)
            mock_process_task.assert_any_call('/mock/books/dir/series2', 1)
            self.assertEqual(mock_process_task.call_count, 2) # Both attempts should be made
            mock_logger.error.assert_called_once() # Verify error was logged for the failed series
            self.assertTrue(result) # The overall task should still report success even if one sub-task failed (due to try-except)
