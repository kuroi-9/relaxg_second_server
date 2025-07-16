from django.db import models
from django.contrib.auth.models import AbstractUser

class CommonUser(AbstractUser):
    # Custom fields
    scan_directory = models.TextField()

    def __str__(self):
        return self.username
