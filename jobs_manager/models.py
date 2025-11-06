from django.db import models

class Job(models.Model):
    # Prototype: Model that represents an upscaling job
    STATUS_CHOICES = [
        ('original', 'Original'),
        ('partial', 'Partial'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    id = models.AutoField(primary_key=True)
    title_name = models.CharField(max_length=255)
    title_path = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # model = models.ForeignKey('Model', on_delete=models.CASCADE)
    used_model_name = models.TextField()
