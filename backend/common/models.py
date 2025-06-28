"""
Models for temporary file uploads.
"""

import json
import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone


class TemporaryFileUpload(models.Model):
    """Track temporary file uploads before they're associated with candidates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_id = models.CharField(max_length=255, unique=True)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    file_size = models.PositiveIntegerField()

    # Storage info (JSON field to store S3 or local storage details)
    storage_info = models.JSONField()

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    # Status
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "temporary_file_uploads"
        indexes = [
            models.Index(fields=["file_id"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["is_used"]),
        ]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Files expire after 1 hour
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if the file upload has expired."""
        return timezone.now() > self.expires_at

    def mark_as_used(self):
        """Mark the file as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()

    def get_storage_info(self):
        """Get storage info as Python dict."""
        if isinstance(self.storage_info, str):
            return json.loads(self.storage_info)
        return self.storage_info

    def __str__(self):
        return f"TempFile: {self.original_filename} ({self.file_id})"
