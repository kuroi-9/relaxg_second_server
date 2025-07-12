from django.db.models import QuerySet
from library.models import Book, BookSeries
from typing import Dict, Any

class BookDBRepository:

    def create_bookseries(self, data: Dict[str, Any]):
        bookseries = BookSeries(**data)
        bookseries.save()
        return bookseries

    # Prototype: Creates a new book record.
    # Pre-conditions: 'data' is a dictionary of book attributes.
    # Post-conditions: Returns the newly created Book instance.
    def create_book(self, data: Dict[str, Any]) -> Book:
        book = Book(**data)
        book.save()
        return book

    # Prototype: Updates an existing book.
    # Pre-conditions: 'book' is the book instance to update, 'data' are the fields to modify.
    # Post-conditions: Returns the updated Book instance.
    def update_book(self, book: Book, data: Dict[str, Any]) -> Book:
        book.file_path = data.get('file_path', book.file_path)
        book.series = data.get('series', book.series)
        book.save()
        return book

    def get_bookseries_by_filepath(self, bookseries_filepath: str) -> BookSeries | None:
        bookseries = BookSeries._default_manager.filter(directory_path=bookseries_filepath).first()
        return bookseries

    # Prototype: Retrieves a book by its ID.
    # Pre-conditions: 'book_id' is the book's ID.
    # Post-conditions: Returns the Book instance or None if not found.
    def get_book_by_id(self, book_id: int) -> Book | None:
        return Book._default_manager.filter(id=book_id).first()

    # Prototype: Retrieves a book by its file path.
    # Pre-conditions: 'file_path' is the complete file path.
    # Post-conditions: Returns the Book instance or None if not found.
    def get_volume_by_file_path(self, file_path: str) -> Book | None:
        return Book._default_manager.filter(file_path=file_path).first()

    # Prototype: Retrieves filtered and sorted books.
    # Pre-conditions: 'filters' is a dictionary of filter criteria, 'order_by' is a string for sorting.
    # Post-conditions: Returns a QuerySet of matching Book objects, ready for pagination.
    def get_books_with_filters_and_order(self, filters: Dict[str, Any], order_by: str) -> QuerySet[Book]:
        pass
