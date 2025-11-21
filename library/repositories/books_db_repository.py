from library.models import Book, Title
from typing import Dict, Any, List

class BooksDBRepository:
    '''BooksDBRepository class provides methods to interact with books and titles in the database.'''

    def create_title(self, data: Dict[str, Any]):
        '''
        Prototype: Creates a new title record.
        Pre-conditions: 'data' is a dictionary of title attributes.
        Post-conditions: Returns the newly created Title instance.
        '''

        title = Title(**data)
        title.save()
        return title

    def delete_title(self, title_id: int) -> bool:
        '''
        Prototype: Deletes a title from the database.
        Pre-conditions: 'title_id' is the ID of the title to delete.
        Post-conditions: Returns True if the title was deleted, False otherwise.
        '''
        try:
            title = Title._default_manager.filter(id=title_id).first()
            if title:
                title.delete()
                return True
            return False
        except Exception as e:
            raise Exception(f"Error deleting title: {e}")


    def create_book(self, data: Dict[str, Any]) -> Book:
        '''
        Prototype: Creates a new book record.
        Pre-conditions: 'data' is a dictionary of book attributes.
        Post-conditions: Returns the newly created Book instance.
        '''

        book = Book(**data)
        book.save()
        return book

    def update_book(self, book: dict) -> Book:
        '''
        Prototype: Updates an existing book.
        Pre-conditions: 'book' is the book instance to update, 'data' are the fields to modify.
        Post-conditions: Returns the updated Book instance.
        '''

        book_instance = Book._default_manager.get(id=book['id'])
        book_instance.status = book["status"]
        book_instance.save()
        return book_instance

    def get_title_by_filepath(self, title_filepath: str) -> Title | None:
        '''
        Retrieves a title by its file path in the database.
        Pre-conditions: 'title_filepath' is the complete file path.
        Post-conditions: Returns the Title instance or None if not found.
        '''

        return Title._default_manager.filter(directory_path=title_filepath).first()

    def get_title_books(self, title_name: str) -> List[Book]:
        '''
        Retrieves all books associated with a title from the database.
        Pre-conditions: 'title_name' is the title of the title.
        Post-conditions: Returns a list of Book instances.
        '''

        return Book._default_manager.filter(title=title_name).all().order_by('title')

    def get_title_books_to_process(self, title_name: str) -> List[Book]:
        '''
        Retrieves all books associated with a title from the database that are not yet processed.
        Pre-conditions: 'title_name' is the title of the title.
        Post-conditions: Returns a list of Book instances.
        '''

        return Book._default_manager.filter(title=title_name).order_by('name')

    def get_book_by_id(self, book_id: int) -> Book | None:
        '''
        Retrieves a book by its ID from the database.
        Pre-conditions: 'book_id' is the book's ID.
        Post-conditions: Returns the Book instance or None if not found.
        '''

        return Book._default_manager.filter(id=book_id).first()

    def get_book_by_file_path(self, file_path: str) -> Book | None:
        '''
        Retrieves a book by its file path from the database.
        Pre-conditions: 'file_path' is the complete file path.
        Post-conditions: Returns the Book instance or None if not found.
        '''

        return Book._default_manager.filter(file_path=file_path).first()

    def get_titles_with_filters_and_order(self, filters: Dict[str, Any], order_by: str) -> List[Title | None]:
        '''
        Retrieves titles filtered and ordered from the database.
        Pre-conditions: 'filters' is a dictionary of filter criteria, 'order_by' is a string for sorting.
        Post-conditions: Returns a List of matching Title objects.
        '''

        try:
            return list(Title._default_manager.filter(**filters).order_by(order_by).values())
        except Exception as e:
            raise Exception(f"Error fetching titles: {e}")

    def get_books_with_filters_and_order(self, filters: Dict[str, Any], order_by: str) -> List[Book | None]:
        '''
        Retrieves books filtered and ordered from the database.
        Pre-conditions: 'filters' is a dictionary of filter criteria, 'order_by' is a string for sorting.
        Post-conditions: Returns a List of matching Book objects.
        '''

        return Book._default_manager.filter(**filters).order_by(order_by).all()

    def get_title_by_id(self, title_id: int) -> Title | None:
        '''
        Retrieves a title by its ID from the database.
        Pre-conditions: 'title_id' is the ID of the title.
        Post-conditions: Returns the Title instance or None if not found.
        '''

        return Title._default_manager.filter(id=title_id).first()
