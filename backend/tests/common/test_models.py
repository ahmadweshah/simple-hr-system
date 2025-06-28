"""
Test models for the common app.
"""

from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from common.models import TemporaryFileUpload
from tests.factories import TemporaryFileUploadFactory


@pytest.mark.django_db
class TestTemporaryFileUploadModel:
    """Test cases for the TemporaryFileUpload model."""

    def test_temporary_file_upload_creation(self):
        """Test creating a temporary file upload."""
        temp_file = TemporaryFileUploadFactory(
            original_filename="test_resume.pdf",
            file_size=1024,
            content_type="application/pdf",
        )

        assert temp_file.id is not None
        assert temp_file.original_filename == "test_resume.pdf"
        assert temp_file.file_size == 1024
        assert temp_file.content_type == "application/pdf"
        assert temp_file.created_at is not None
        assert temp_file.file_id is not None
        assert temp_file.storage_info is not None
        assert not temp_file.is_used
        assert temp_file.used_at is None

    def test_string_representation(self):
        """Test the string representation of temporary file upload."""
        temp_file = TemporaryFileUploadFactory(original_filename="resume.pdf")
        expected = f"TempFile: {temp_file.original_filename} ({temp_file.file_id})"
        assert str(temp_file) == expected

    def test_is_expired_method(self):
        """Test the is_expired method."""
        # Create a file that's not expired (recent)
        recent_file = TemporaryFileUploadFactory()
        assert not recent_file.is_expired()

        # Create a file that's expired (older than expires_at)
        expired_file = TemporaryFileUploadFactory()
        # Manually set the expires_at to past time
        expired_file.expires_at = timezone.now() - timedelta(hours=1)
        expired_file.save()

        assert expired_file.is_expired()

    def test_auto_expires_at_setting(self):
        """Test that expires_at is automatically set when not provided."""
        temp_file = TemporaryFileUploadFactory(expires_at=None)
        temp_file.save()

        # Should be set to approximately 1 hour from now
        expected_expiry = timezone.now() + timedelta(hours=1)
        time_diff = abs((temp_file.expires_at - expected_expiry).total_seconds())
        assert time_diff < 60  # Within 60 seconds of expected time

    def test_mark_as_used_method(self):
        """Test the mark_as_used method."""
        temp_file = TemporaryFileUploadFactory()
        assert not temp_file.is_used
        assert temp_file.used_at is None

        temp_file.mark_as_used()

        assert temp_file.is_used
        assert temp_file.used_at is not None
        assert temp_file.used_at <= timezone.now()

    def test_get_storage_info_method(self):
        """Test the get_storage_info method."""
        storage_data = {
            "storage_type": "s3",
            "s3_bucket": "test-bucket",
            "s3_key": "test-key",
        }
        temp_file = TemporaryFileUploadFactory(storage_info=storage_data)

        retrieved_info = temp_file.get_storage_info()
        assert retrieved_info == storage_data
        assert isinstance(retrieved_info, dict)

    def test_file_size_validation(self):
        """Test file size validation."""
        # Valid file size
        temp_file = TemporaryFileUploadFactory(file_size=1024)
        temp_file.full_clean()  # Should not raise

        # Test with negative file size (should be invalid)
        with pytest.raises(ValidationError):
            invalid_file = TemporaryFileUploadFactory.build(file_size=-1)
            invalid_file.full_clean()

    def test_content_type_validation(self):
        """Test content type validation."""
        # Valid content types
        valid_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ]

        for content_type in valid_types:
            temp_file = TemporaryFileUploadFactory(content_type=content_type)
            temp_file.full_clean()  # Should not raise

    def test_file_id_uniqueness(self):
        """Test that file_id is unique."""
        file_id = "unique-test-id"
        TemporaryFileUploadFactory(file_id=file_id)

        # Trying to create another with same file_id should fail
        with pytest.raises(Exception):  # IntegrityError for unique constraint
            TemporaryFileUploadFactory(file_id=file_id)

    def test_ordering(self):
        """Test that temporary files can be ordered by creation time."""
        file1 = TemporaryFileUploadFactory()
        file2 = TemporaryFileUploadFactory()
        file3 = TemporaryFileUploadFactory()

        # Order by created_at descending (newest first)
        files = TemporaryFileUpload.objects.all().order_by("-created_at")
        assert files[0] == file3  # Most recent first
        assert files[1] == file2
        assert files[2] == file1

    def test_json_storage_info_handling(self):
        """Test handling of JSON string in storage_info."""
        import json

        storage_data = {"storage_type": "local", "path": "/tmp/test"}
        temp_file = TemporaryFileUploadFactory()

        # Set storage_info as JSON string
        temp_file.storage_info = json.dumps(storage_data)
        temp_file.save()

        # get_storage_info should handle both dict and string
        retrieved_info = temp_file.get_storage_info()
        assert retrieved_info == storage_data

    def test_expired_files_query(self):
        """Test querying for expired files."""
        # Clear existing data to ensure clean test
        TemporaryFileUpload.objects.all().delete()

        # Create some recent files
        TemporaryFileUploadFactory.create_batch(3)

        # Create some expired files
        expired_files = TemporaryFileUploadFactory.create_batch(2)
        for expired_file in expired_files:
            expired_file.expires_at = timezone.now() - timedelta(hours=1)
            expired_file.save()

        # Query for expired files
        now = timezone.now()
        expired_queryset = TemporaryFileUpload.objects.filter(expires_at__lt=now)

        assert expired_queryset.count() == 2
        assert all(f.is_expired() for f in expired_queryset)

    def test_used_files_query(self):
        """Test querying for used vs unused files."""
        # Clear existing data to ensure clean test
        TemporaryFileUpload.objects.all().delete()

        # Create unused files
        TemporaryFileUploadFactory.create_batch(3)

        # Create used files
        TemporaryFileUploadFactory.create_batch(2, is_used=True)

        assert TemporaryFileUpload.objects.filter(is_used=False).count() == 3
        assert TemporaryFileUpload.objects.filter(is_used=True).count() == 2
