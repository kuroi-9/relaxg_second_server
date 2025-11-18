from django.db import models

class Book(models.Model):
    STATUS = (
        ('original', 'Original'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    )
    # Prototype: Model that represents a book (most specifically a single volume of a title) in the library.
    # Pre-condition: None.
    # Post-condition: Defines the structure of a book's data.
    id = models.AutoField(primary_key=True)
    name = models.TextField(default='', unique=True)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, blank=True, null=True, unique=True)
    title = models.ForeignKey('Title', on_delete=models.SET_NULL, to_field='name', blank=True, null=True)
    file_path = models.TextField(default='d')
    status = models.CharField(max_length=50, default='original') # SCANNED, PROCESSED

class Title(models.Model):
    # Prototype: Model that represents a series of books.
    # Pre-condition: None.
    # Post-condition: Defines the structure of a title's data.
    id = models.AutoField(primary_key=True)
    name = models.TextField(default='', unique=True)
    directory_path = models.TextField(default='')
    description = models.TextField(blank=True, null=True)
    cover_image = models.TextField(blank=True, null=True)
