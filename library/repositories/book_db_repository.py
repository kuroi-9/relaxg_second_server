from django.db.models import QuerySet
from library.models import Book, BookSeries
from typing import Dict, Any

class BookDBRepository:
    def create_bookseries(self, data: Dict[str, Any]):
        '''
        Prototype: Creates a new bookseries record.
        Pre-conditions: 'data' is a dictionary of bookseries attributes.
        Post-conditions: Returns the newly created BookSeries instance.
        '''

        bookseries = BookSeries(**data)
        bookseries.save()
        return bookseries

    def create_book(self, data: Dict[str, Any]) -> Book:
        '''
        Prototype: Creates a new book record.
        Pre-conditions: 'data' is a dictionary of book attributes.
        Post-conditions: Returns the newly created Book instance.
        '''

        book = Book(**data)
        book.save()
        return book


    def update_book(self, book: Book, data: Dict[str, Any]) -> Book:
        '''
        Prototype: Updates an existing book.
        Pre-conditions: 'book' is the book instance to update, 'data' are the fields to modify.
        Post-conditions: Returns the updated Book instance.
        '''

        book.file_path = data.get('file_path', book.file_path)
        book.series = data.get('series', book.series)
        book.save()
        return book

    def get_bookseries_by_filepath(self, bookseries_filepath: str) -> BookSeries | None:
        '''
        Retrieves a book series by its file path in the database.
        Pre-conditions: 'bookseries_filepath' is the complete file path.
        Post-conditions: Returns the BookSeries instance or None if not found.
        '''

        bookseries = BookSeries._default_manager.filter(directory_path=bookseries_filepath).first()
        return bookseries

    def get_book_by_id(self, book_id: int) -> Book | None:
        '''
        Retrieves a book by its ID from the database.
        Pre-conditions: 'book_id' is the book's ID.
        Post-conditions: Returns the Book instance or None if not found.
        '''

        return Book._default_manager.filter(id=book_id).first()

    def get_volume_by_file_path(self, file_path: str) -> Book | None:
        '''
        Retrieves a book volume by its file path from the database.
        Pre-conditions: 'file_path' is the complete file path.
        Post-conditions: Returns the Book instance or None if not found.
        '''

        return Book._default_manager.filter(file_path=file_path).first()

    # Prototype: Retrieves filtered and sorted books.
    # Pre-conditions: 'filters' is a dictionary of filter criteria, 'order_by' is a string for sorting.
    # Post-conditions: Returns a QuerySet of matching Book objects, ready for pagination.
    def get_books_with_filters_and_order(self, filters: Dict[str, Any], order_by: str) -> QuerySet[Book]:
        pass
