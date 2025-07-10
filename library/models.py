from django.db import models
from django.conf import settings

class Book(models.Model):
    # Prototype: Model that represents a book (most specifically a single volume) in the library.
    # Pre-condition: None.
    # Post-condition: Defines the structure of a book's data.
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, blank=True, null=True, unique=True)
    series = models.ForeignKey('BookSeries', on_delete=models.SET_NULL, to_field='title', blank=True, null=True)
    file_path = models.TextField(default='d')
    status = models.CharField(max_length=50, default='PENDING_SCAN') # Ex: PENDING_SCAN, SCANNED, METADATA_EXTRACTED, ENRICHED, READY
    # ... other metadata fields, processing status, etc.
    # Note: No direct link to the upscaled file here, access will be via the `upscale_processor_app` application.

class BookSeries(models.Model):
    # Prototype: Model that represents a series of books.
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True, default='')
    directory_path = models.TextField(default='')
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='series_covers/', blank=True, null=True)
    # ... other metadata fields, processing status, etc.

class UserProfile(models.Model):
    # Prototype: Model for user profiles, linked to the Django user.
    # Pre-condition: None.
    # Post-condition: Defines the structure of a user's profile.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # ... specific profile fields (e.g., default_scan_directory)
