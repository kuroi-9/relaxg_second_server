from rest_framework import serializers
from .models import Book

class BookListSerializer(serializers.ModelSerializer):
    # Prototype: Serializer that displays a list of books.
    # Pre-conditions: Instance(s) of Book.
    # Post-conditions: Dictionary(s) containing relevant fields for list display.
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'status']

class BookDetailSerializer(serializers.ModelSerializer):
    # Prototype: Serializer for displaying full details of a book.
    # Pre-conditions: Instance of Book.
    # Post-conditions: Dictionary containing all details of the book.
    class Meta:
        model = Book
        fields = '__all__'

class BookScanRequestSerializer(serializers.Serializer):
    # Prototype: Serializer for validating a directory scan request.
    # Pre-conditions: Dictionary of data for the scan request.
    # Post-conditions: Validated dictionary containing the directory path to scan.
    scan_directory_path = serializers.CharField(max_length=500, required=False, help_text="Path of the directory to scan. If empty, uses the default directory of the user.")

class BookUpscaleRequestSerializer(serializers.Serializer):
    # Prototype: Serializer for validating an upscale request for a book.
    # Pre-conditions: Dictionary of data for the upscale request.
    # Post-conditions: Validated dictionary containing 'book_id' and 'preset_name'.
    book_id = serializers.IntegerField(help_text="ID of the book to upscale.")
    preset_name = serializers.CharField(max_length=100, default='default', help_text="Name of the upscale preset to use.")
