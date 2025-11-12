from django.db import models

class Job(models.Model):
    # Prototype: Model that represents an upscaling job
    STATUS_CHOICES = [
        ('original', 'Original'),
        ('partial', 'Partial'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    STEPS = [
        ('scanning', 'Scanning'),
        ('extraction', 'Extraction'),
        ('resizing', 'Resizing'),
        ('enhancement', 'Enhancement'),
        ('finalization', 'Finalization')
    ]

    id = models.AutoField(primary_key=True)
    title_name = models.CharField(max_length=255)
    title_path = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    images_number = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    step = models.CharField(max_length=20, choices=STEPS, default='extraction')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    used_model_name = models.TextField()
