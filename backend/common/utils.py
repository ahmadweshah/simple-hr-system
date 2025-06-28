"""
Utility functions for file handling and validation.
"""

import os

import magic
from django.core.exceptions import ValidationError


def validate_file_type(file, allowed_types):
    """
    Validate file type using python-magic.

    Args:
        file: Django UploadedFile object
        allowed_types: List of allowed MIME types

    Raises:
        ValidationError: If file type is not allowed
    """
    if not file:
        raise ValidationError("No file provided")

    # Get file MIME type
    file_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # Reset file pointer

    if file_type not in allowed_types:
        raise ValidationError(
            f"File type {file_type} not allowed. Allowed types: {', '.join(allowed_types)}"
        )


def validate_file_size(file, max_size_mb=5):
    """
    Validate file size.

    Args:
        file: Django UploadedFile object
        max_size_mb: Maximum file size in MB

    Raises:
        ValidationError: If file is too large
    """
    if not file:
        raise ValidationError("No file provided")

    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(f"File too large. Maximum size: {max_size_mb}MB")


def get_resume_upload_path(instance, filename):
    """
    Generate upload path for resume files.

    Args:
        instance: Model instance
        filename: Original filename

    Returns:
        str: Upload path
    """
    # Create structured path: resumes/{candidate_id}/filename
    candidate_id = instance.id or "temp"
    file_extension = os.path.splitext(filename)[1]
    return f"resumes/{candidate_id}/resume{file_extension}"
