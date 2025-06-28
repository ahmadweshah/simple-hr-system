from datetime import date

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from factory.django import DjangoModelFactory

from candidates.models import ApplicationStatus, Candidate, Department, StatusHistory
from common.models import TemporaryFileUpload


class CandidateFactory(DjangoModelFactory):
    """Factory for creating Candidate instances."""

    class Meta:
        model = Candidate

    full_name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"candidate{n}@example.com")
    phone = factory.Sequence(lambda n: f"+123456789{n:03d}")
    date_of_birth = factory.Faker(
        "date_between", start_date=date(1980, 1, 1), end_date=date(2000, 12, 31)
    )
    years_of_experience = factory.Faker("random_int", min=0, max=15)
    department = factory.Faker(
        "random_element", elements=[choice[0] for choice in Department.choices]
    )
    resume_file_id = factory.Faker("uuid4")
    resume_filename = factory.Faker("file_name", extension="pdf")
    resume_url = factory.Faker("url")
    current_status = ApplicationStatus.SUBMITTED


class ITCandidateFactory(CandidateFactory):
    """Factory for IT department candidates."""

    department = Department.IT
    years_of_experience = factory.Faker("random_int", min=2, max=10)


class HRCandidateFactory(CandidateFactory):
    """Factory for HR department candidates."""

    department = Department.HR
    years_of_experience = factory.Faker("random_int", min=1, max=8)


class FinanceCandidateFactory(CandidateFactory):
    """Factory for Finance department candidates."""

    department = Department.FINANCE
    years_of_experience = factory.Faker("random_int", min=1, max=12)


class StatusHistoryFactory(DjangoModelFactory):
    """Factory for creating StatusHistory instances."""

    class Meta:
        model = StatusHistory

    candidate = factory.SubFactory(CandidateFactory)
    status = factory.Faker(
        "random_element", elements=[choice[0] for choice in ApplicationStatus.choices]
    )
    feedback = factory.Faker("text", max_nb_chars=200)
    admin_info = factory.Faker("name")


class TemporaryFileUploadFactory(DjangoModelFactory):
    """Factory for creating TemporaryFileUpload instances."""

    class Meta:
        model = TemporaryFileUpload

    file_id = factory.Faker("uuid4")
    original_filename = factory.Faker("file_name", extension="pdf")
    content_type = "application/pdf"
    file_size = factory.Faker("random_int", min=1024, max=5242880)  # 1KB to 5MB
    storage_info = factory.LazyAttribute(
        lambda obj: {
            "storage_type": "local",
            "local_path": f"temp/{obj.file_id}.pdf",
            "file_id": obj.file_id,
            "filename": obj.original_filename,
        }
    )
    is_used = False


def create_test_file(filename="test_resume.pdf", content=b"PDF content"):
    """Create a test file for upload testing."""
    return SimpleUploadedFile(filename, content, content_type="application/pdf")


def create_candidate_with_history(status_count=3):
    """Create a candidate with multiple status history entries."""
    candidate = CandidateFactory()

    statuses = [
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.INTERVIEW_SCHEDULED,
        ApplicationStatus.ACCEPTED,
    ]

    for i in range(min(status_count, len(statuses))):
        StatusHistoryFactory(candidate=candidate, status=statuses[i])
        candidate.current_status = statuses[i]

    candidate.save()
    return candidate
