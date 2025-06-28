"""
Simplified test views for the common app.
"""

from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient


class TestFileUploadViewSimple(TestCase):
    """Simplified test cases for file upload endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.url = "/api/upload/"

    @patch("common.views.validate_file_size")
    @patch("common.views.validate_file_type")
    @patch("common.views.FileUploadService")
    def test_upload_with_mocked_service(
        self, mock_service_class, mock_validate_type, mock_validate_size
    ):
        """Test file upload with mocked service."""
        # Setup mocks
        mock_validate_type.return_value = None  # No exception
        mock_validate_size.return_value = None  # No exception

        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.upload_resume.return_value = {
            "file_id": "test-file-id",
            "url": "http://example.com/test.pdf",
            "filename": "test.pdf",
        }

        # Create test file
        test_file = SimpleUploadedFile(
            "test.pdf", b"PDF content", content_type="application/pdf"
        )

        # Make request
        response = self.client.post(self.url, {"file": test_file}, format="multipart")

        # Assert response
        self.assertEqual(response.status_code, 200)
        self.assertIn("file_id", response.json())

    def test_upload_without_file(self):
        """Test upload request without file."""
        response = self.client.post(self.url, {}, format="multipart")
        self.assertEqual(response.status_code, 400)
