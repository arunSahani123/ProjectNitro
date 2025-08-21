import uuid
import os
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class FileUpload(models.Model):
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    filename = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    progress = models.IntegerField(default=0)
    parsed_content = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_name} ({self.status})"
    
    def delete(self, *args, **kwargs):
        # Delete the file from filesystem when deleting the record
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)
    
    @property
    def file_url(self):
        if self.file:
            return f"{settings.MEDIA_URL}{self.file.name}"
        return None