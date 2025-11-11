from django.test import TestCase
from library.models import Book, Title
from library.repositories.books_db_repository import BooksDBRepository

class BooksDBRepositoryTest(TestCase):
    def setUp(self):
        self.repository = BooksDBRepository()
        self.title_data = {
            'name': 'Test Series',
            'directory_path': '/path/to/test/series',
            'cover_image': None # Corresponds to ImageField(blank=True, null=True)
        }
        self.book_data = {
            'id': 1,
            'name': 'Test Book 1',
            'author': 'Test Author', # Added as per models.py
            'file_path': '/path/to/test/series/book1.pdf',
            'status': 'SCANNED' # Added as per models.py default
        }

    def tearDown(self):
        Book._default_manager.all().delete()
        Title._default_manager.all().delete()

    def test_create_title(self):
        titles = self.repository.create_title(self.title_data)
        self.assertIsInstance(titles, Title)
        self.assertEqual(titles.name, 'Test Series')
        self.assertEqual(titles.directory_path, '/path/to/test/series')
        self.assertEqual(Title._default_manager.count(), 1)

    def test_create_book(self):
        book = self.repository.create_book(self.book_data)
        self.assertIsInstance(book, Book)
        self.assertEqual(book.name, 'Test Book 1')
        self.assertEqual(book.file_path, '/path/to/test/series/book1.pdf')
        self.assertEqual(Book._default_manager.count(), 1)

    def test_update_book(self):
        initial_book = self.repository.create_book(self.book_data)
        update_data = {
            'file_path': '/new/path/to/test/series/book1_updated.pdf',
            'title': None # This tests setting series to None if it was previously set, or keeping it None
        }
        updated_book = self.repository.update_book(initial_book, update_data)
        self.assertEqual(updated_book.file_path, '/new/path/to/test/series/book1_updated.pdf')
        self.assertIsNone(updated_book.title)
        self.assertEqual(Book._default_manager.count(), 1) # Ensure no new book is created

        # Test updating with an actual series
        title = self.repository.create_title(self.title_data)
        update_data_with_series = {
            'title': title
        }
        updated_book_with_series = self.repository.update_book(updated_book, update_data_with_series)
        self.assertEqual(updated_book_with_series.title, title)

    def test_get_titles_by_filepath(self):
        self.repository.create_title(self.title_data)
        found_series = self.repository.get_title_by_filepath('/path/to/test/series')
        self.assertIsNotNone(found_series)
        if found_series is not None:
            self.assertEqual(found_series.name, 'Test Series')

        not_found_series = self.repository.get_title_by_filepath('/path/to/non/existent/series')
        self.assertIsNone(not_found_series)

    def test_get_book_by_id(self):
        book = self.repository.create_book(self.book_data)
        self.assertIsNotNone(book)
        self.assertIsNotNone(book.id)
        found_book = self.repository.get_book_by_id(int(self.book_data["id"]))
        self.assertIsNotNone(found_book)
        if found_book is not None:
            self.assertEqual(found_book.name, 'Test Book 1')

        not_found_book = self.repository.get_book_by_id(999) # Non-existent ID
        self.assertIsNone(not_found_book)

    def test_get_volume_by_file_path(self):
        self.repository.create_book(self.book_data)
        found_book = self.repository.get_book_by_file_path('/path/to/test/series/book1.pdf')
        self.assertIsNotNone(found_book)
        if found_book is not None:
            self.assertEqual(found_book.name, 'Test Book 1')

        not_found_book = self.repository.get_book_by_file_path('/path/to/non/existent/book.pdf')
        self.assertIsNone(not_found_book)

    def test_get_titles_with_filters_and_order(self):
        #TODO: Implement filters and order + pagination first
        pass
    def test_get_books_with_filters_and_order(self):
        #TODO: Implement filters and order + pagination first
        pass
