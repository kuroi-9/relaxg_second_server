from library.models import Book
from typing import Dict, Any
from django.db.models import QuerySet

class BookDBRepository:
    # Prototype: Creates a new book record.
    # Pre-conditions: 'data' is a dictionary of book attributes.
    # Post-conditions: Returns the newly created Book instance.
    def create_book(self, data: Dict[str, Any]) -> Book:
        pass

    # Prototype: Updates an existing book.
    # Pre-conditions: 'book' is the book instance to update, 'data' are the fields to modify.
    # Post-conditions: Returns the updated Book instance.
    def update_book(self, book: Book, data: Dict[str, Any]) -> Book:
        pass

    # Prototype: Retrieves a book by its ID.
    # Pre-conditions: 'book_id' is the book's ID.
    # Post-conditions: Returns the Book instance or None if not found.
    def get_book_by_id(self, book_id: int) -> Book | None:
        pass

    # Prototype: Retrieves a book by its file path.
    # Pre-conditions: 'file_path' is the complete file path.
    # Post-conditions: Returns the Book instance or None if not found.
    def get_book_by_file_path(self, file_path: str) -> Book | None:
        pass

    # Prototype: Retrieves filtered and sorted books.
    # Pre-conditions: 'filters' is a dictionary of filter criteria, 'order_by' is a string for sorting.
    # Post-conditions: Returns a QuerySet of matching Book objects, ready for pagination.
    def get_books_with_filters_and_order(self, filters: Dict[str, Any], order_by: str) -> QuerySet[Book]:
        pass
