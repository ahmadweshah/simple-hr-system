"""
Test models for the candidates app.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from faker import Faker

from candidates.models import ApplicationStatus, Candidate, Department, StatusHistory
from tests.factories import CandidateFactory, StatusHistoryFactory


@pytest.mark.django_db
class TestCandidateModel:
    """Test cases for the Candidate model."""

    def test_candidate_creation(self):
        """Test creating a candidate with valid data."""
        candidate = CandidateFactory()
        assert candidate.id is not None
        assert candidate.full_name
        assert candidate.email
        assert candidate.phone
        assert candidate.department in [choice[0] for choice in Department.choices]
        assert candidate.current_status == ApplicationStatus.SUBMITTED
        assert candidate.created_at is not None
        assert candidate.updated_at is not None

    def test_candidate_string_representation(self):
        """Test the string representation of a candidate."""
        full_name = Faker().name()

        candidate = CandidateFactory(full_name=full_name, department=Department.IT)
        assert str(candidate) == f"{full_name} - IT"

    def test_email_uniqueness(self):
        """Test that email must be unique."""
        email = Faker().email()

        CandidateFactory(email=email)

        with pytest.raises(IntegrityError):
            CandidateFactory(email=email)

    def test_phone_uniqueness(self):
        """Test that phone must be unique."""

        phone_number = Faker().basic_phone_number()

        CandidateFactory(phone=phone_number)

        with pytest.raises(IntegrityError):
            CandidateFactory(phone=phone_number)

    def test_email_case_insensitive_validation(self):
        """Test that email validation is case-insensitive."""

        email = Faker().email()
        CandidateFactory(email=email)

        # Create another candidate with same email but different case
        duplicate_candidate = CandidateFactory.build(email=email.upper())

        with pytest.raises(ValidationError):
            duplicate_candidate.clean()

    def test_department_choices(self):
        """Test that only valid departments are accepted."""
        for department_choice in Department.choices:
            candidate = CandidateFactory(department=department_choice[0])
            assert candidate.department == department_choice[0]

    def test_status_choices(self):
        """Test that only valid statuses are accepted."""
        for status_choice in ApplicationStatus.choices:
            candidate = CandidateFactory(current_status=status_choice[0])
            assert candidate.current_status == status_choice[0]

    def test_years_of_experience_validation(self):
        """Test years of experience validation."""
        # Valid experience
        candidate = CandidateFactory(years_of_experience=5)
        candidate.full_clean()

        # Test negative experience at the database level
        with pytest.raises(IntegrityError):
            candidate = CandidateFactory.build(years_of_experience=-1)
            candidate.save()

    def test_candidate_ordering(self):
        """Test that candidates are ordered by creation date (newest first)."""
        candidate1 = CandidateFactory()
        candidate2 = CandidateFactory()
        candidate3 = CandidateFactory()

        candidates = Candidate.objects.all()
        assert candidates[0] == candidate3  # Most recent first
        assert candidates[1] == candidate2
        assert candidates[2] == candidate1


@pytest.mark.django_db
class TestStatusHistoryModel:
    """Test cases for the StatusHistory model."""

    def test_status_history_creation(self):
        """Test creating a status history entry."""
        candidate = CandidateFactory()
        history = StatusHistoryFactory(
            candidate=candidate,
            status=ApplicationStatus.UNDER_REVIEW,
            feedback="Good candidate",
        )

        assert history.candidate == candidate
        assert history.status == ApplicationStatus.UNDER_REVIEW
        assert history.feedback == "Good candidate"
        assert history.changed_at is not None

    def test_status_history_string_representation(self):
        """Test the string representation of status history."""

        name = Faker().name()
        candidate = CandidateFactory(full_name=name)
        history = StatusHistoryFactory(
            candidate=candidate, status=ApplicationStatus.INTERVIEW_SCHEDULED
        )

        expected = (
            f"{name} - {ApplicationStatus.INTERVIEW_SCHEDULED} - {history.changed_at}"
        )
        assert str(history) == expected

    def test_status_history_ordering(self):
        """Test that status history is ordered by changed_at (newest first)."""
        candidate = CandidateFactory()

        history1 = StatusHistoryFactory(
            candidate=candidate, status=ApplicationStatus.SUBMITTED
        )
        history2 = StatusHistoryFactory(
            candidate=candidate, status=ApplicationStatus.UNDER_REVIEW
        )
        history3 = StatusHistoryFactory(
            candidate=candidate, status=ApplicationStatus.INTERVIEW_SCHEDULED
        )

        histories = candidate.status_history.all()
        assert histories[0] == history3  # Most recent first
        assert histories[1] == history2
        assert histories[2] == history1

    def test_status_history_cascade_delete(self):
        """Test that status history is deleted when candidate is deleted."""
        candidate = CandidateFactory()
        history = StatusHistoryFactory(candidate=candidate)

        candidate_id = candidate.id
        history_id = history.id

        candidate.delete()

        assert not Candidate.objects.filter(id=candidate_id).exists()
        assert not StatusHistory.objects.filter(id=history_id).exists()

    def test_multiple_status_changes(self):
        """Test creating multiple status changes for a candidate."""
        candidate = CandidateFactory()

        # Create status progression
        statuses = [
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.INTERVIEW_SCHEDULED,
            ApplicationStatus.ACCEPTED,
        ]

        histories = []
        for status in statuses:
            history = StatusHistoryFactory(candidate=candidate, status=status)
            histories.append(history)

        assert candidate.status_history.count() == 4

        # Check they're in reverse chronological order
        retrieved_histories = list(candidate.status_history.all())
        assert retrieved_histories[0] == histories[-1]  # Most recent first
