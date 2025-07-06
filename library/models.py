from django.db import models
from django.conf import settings

class Book(models.Model):
    # Prototype: Model that represents a book in the library.
    # Pre-condition: None.
    # Post-condition: Defines the structure of a book's data.
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, blank=True, null=True, unique=True)
    file_path = models.TextField() # Path to the original file
    status = models.CharField(max_length=50, default='PENDING_SCAN') # Ex: PENDING_SCAN, SCANNED, METADATA_EXTRACTED, ENRICHED, READY
    # ... other metadata fields, processing status, etc.
    # Note: No direct link to the upscaled file here, access will be via the `upscale_processor_app` application.

class UserProfile(models.Model):
    # Prototype: Model for user profiles, linked to the Django user.
    # Pre-condition: None.
    # Post-condition: Defines the structure of a user's profile.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # ... specific profile fields (e.g., default_scan_directory)
