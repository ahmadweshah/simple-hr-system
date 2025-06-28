"""
Pytest configuration and fixtures.
"""

import os

import django
import pytest
from django.conf import settings


def pytest_configure(config):
    """Configure Django settings for pytest."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()

    # Register custom markers
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "api: marks tests as API tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")


@pytest.fixture(scope="session")
def django_db_setup():
    """Set up the Django database for testing."""
    # Use in-memory SQLite for tests
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Give all tests access to the database.

    This fixture is automatically used for all tests,
    removing the need to add @pytest.mark.django_db to every test.
    """
    pass


@pytest.fixture
def api_client():
    """Provide a DRF API client for testing."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def admin_api_client():
    """Provide a DRF API client with admin header for testing."""
    from rest_framework.test import APIClient

    client = APIClient()
    client.defaults["HTTP_X_ADMIN"] = "1"
    return client


@pytest.fixture
def sample_candidate():
    """Create a sample candidate for testing."""
    from tests.factories import CandidateFactory

    return CandidateFactory()


@pytest.fixture
def sample_candidates():
    """Create multiple sample candidates for testing."""
    from tests.factories import CandidateFactory

    return CandidateFactory.create_batch(5)


@pytest.fixture
def candidate_with_history():
    """Create a candidate with status history for testing."""
    from tests.factories import create_candidate_with_history

    return create_candidate_with_history(3)


@pytest.fixture
def temp_file():
    """Create a temporary file upload for testing."""
    from tests.factories import TemporaryFileUploadFactory

    return TemporaryFileUploadFactory()


@pytest.fixture
def pdf_file():
    """Create a test PDF file for upload testing."""
    from tests.factories import create_test_file

    return create_test_file("test_resume.pdf", b"%PDF-1.4 fake pdf content")


@pytest.fixture
def docx_file():
    """Create a test DOCX file for upload testing."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile(
        "test_resume.docx",
        b"PK fake docx content",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@pytest.fixture
def invalid_file():
    """Create an invalid file for testing."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile(
        "test_resume.txt", b"This is a text file", content_type="text/plain"
    )


@pytest.fixture
def large_file():
    """Create a large file (over 5MB) for testing."""
    from tests.factories import create_test_file

    # Create a 6MB file
    large_content = b"x" * (6 * 1024 * 1024)
    return create_test_file("large_resume.pdf", large_content)


@pytest.fixture(scope="function")
def clean_media():
    """Clean up media files after each test."""
    yield
    # Cleanup code here if needed
    import os

    from django.conf import settings

    media_root = settings.MEDIA_ROOT
    if os.path.exists(media_root):
        # Clean up test files but keep the directory structure
        for root, dirs, files in os.walk(media_root):
            for file in files:
                if file.startswith("test_"):
                    os.remove(os.path.join(root, file))


# Database fixtures for specific test scenarios
@pytest.fixture
def empty_database():
    """Ensure database is empty for specific tests."""
    from candidates.models import Candidate, StatusHistory
    from common.models import TemporaryFileUpload

    # Clear all data
    StatusHistory.objects.all().delete()
    Candidate.objects.all().delete()
    TemporaryFileUpload.objects.all().delete()


@pytest.fixture
def database_with_candidates():
    """Create a database with various candidates for complex testing."""
    from candidates.models import ApplicationStatus, Department
    from tests.factories import CandidateFactory

    # Create candidates for each department
    it_candidates = CandidateFactory.create_batch(3, department=Department.IT)
    hr_candidates = CandidateFactory.create_batch(2, department=Department.HR)
    finance_candidates = CandidateFactory.create_batch(2, department=Department.FINANCE)

    # Create candidates with different statuses
    CandidateFactory.create_batch(2, current_status=ApplicationStatus.UNDER_REVIEW)
    CandidateFactory.create_batch(
        1, current_status=ApplicationStatus.INTERVIEW_SCHEDULED
    )
    CandidateFactory.create_batch(1, current_status=ApplicationStatus.ACCEPTED)
    CandidateFactory.create_batch(1, current_status=ApplicationStatus.REJECTED)

    return {
        "it_candidates": it_candidates,
        "hr_candidates": hr_candidates,
        "finance_candidates": finance_candidates,
        "total_count": 12,
    }
