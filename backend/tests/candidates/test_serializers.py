"""
Test serializers for the candidates app.
"""

from unittest.mock import patch

import pytest
from faker import Faker

from candidates.models import ApplicationStatus, Department
from candidates.serializers import (
    CandidateListSerializer,
    CandidateRegistrationSerializer,
    CandidateStatusSerializer,
    StatusUpdateSerializer,
)
from tests.factories import (
    CandidateFactory,
    TemporaryFileUploadFactory,
    create_candidate_with_history,
)


@pytest.mark.django_db
class TestCandidateRegistrationSerializer:
    """Test cases for CandidateRegistrationSerializer."""

    @patch("common.storage.FileUploadService.move_temp_file_to_permanent")
    def test_valid_serializer_data(self, mock_move_file):
        """Test serializer with valid data."""
        # Mock the file moving service
        mock_move_file.return_value = "http://example.com/permanent/resume.pdf"

        temp_file = TemporaryFileUploadFactory()

        email = Faker().email()
        phone_number = Faker().basic_phone_number()

        data = {
            "full_name": "John Doe",
            "email": email,
            "phone": phone_number,
            "date_of_birth": "1990-01-15",
            "years_of_experience": 5,
            "department": Department.IT,
            "file_id": temp_file.file_id,
        }

        serializer = CandidateRegistrationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        assert serializer.is_valid()

        candidate = serializer.save()
        assert candidate.full_name == "John Doe"
        assert candidate.email == email
        assert candidate.phone == phone_number
        assert candidate.department == Department.IT
        assert candidate.current_status == ApplicationStatus.SUBMITTED

        # Verify file service was called
        mock_move_file.assert_called_once()

        # Verify temp file was marked as used
        temp_file.refresh_from_db()
        assert temp_file.is_used

    def test_invalid_email_format(self):
        """Test serializer with invalid email format."""
        temp_file = TemporaryFileUploadFactory()

        data = {
            "full_name": "John Doe",
            "email": "invalid-email",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-15",
            "years_of_experience": 5,
            "department": Department.IT,
            "file_id": temp_file.file_id,
        }

        serializer = CandidateRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_duplicate_email(self):
        """Test serializer with duplicate email."""
        existing_candidate = CandidateFactory(email="existing@example.com")
        temp_file = TemporaryFileUploadFactory()

        data = {
            "full_name": "John Doe",
            "email": "existing@example.com",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-15",
            "years_of_experience": 5,
            "department": Department.IT,
            "file_id": temp_file.file_id,
        }

        serializer = CandidateRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_duplicate_phone(self):
        """Test serializer with duplicate phone."""
        phone_number = "+1234567891"  # Use different number
        existing_candidate = CandidateFactory(phone=phone_number)
        temp_file = TemporaryFileUploadFactory()

        data = {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": phone_number,
            "date_of_birth": "1990-01-15",
            "years_of_experience": 5,
            "department": Department.IT,
            "file_id": temp_file.file_id,
        }

        serializer = CandidateRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "phone" in serializer.errors

    def test_invalid_department(self):
        """Test serializer with invalid department."""
        temp_file = TemporaryFileUploadFactory()

        data = {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-15",
            "years_of_experience": 5,
            "department": "INVALID_DEPT",
            "file_id": temp_file.file_id,
        }

        serializer = CandidateRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "department" in serializer.errors

    def test_negative_experience(self):
        """Test serializer with negative years of experience."""
        temp_file = TemporaryFileUploadFactory()

        data = {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-15",
            "years_of_experience": -1,
            "department": Department.IT,
            "file_id": temp_file.file_id,
        }

        serializer = CandidateRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "years_of_experience" in serializer.errors

    def test_missing_required_fields(self):
        """Test serializer with missing required fields."""
        data = {
            "full_name": "John Doe",
            # Missing other required fields
        }

        serializer = CandidateRegistrationSerializer(data=data)
        assert not serializer.is_valid()

        required_fields = [
            "email",
            "phone",
            "date_of_birth",
            "years_of_experience",
            "department",
            "file_id",
        ]
        for field in required_fields:
            assert field in serializer.errors


@pytest.mark.django_db
class TestCandidateStatusSerializer:
    """Test cases for CandidateStatusSerializer."""

    def test_serializer_output(self):
        """Test serializer output format."""
        candidate = create_candidate_with_history(3)

        serializer = CandidateStatusSerializer(candidate)
        data = serializer.data

        assert data["id"] == str(candidate.id)
        assert data["full_name"] == candidate.full_name
        assert data["current_status"] == candidate.current_status
        assert "status_history" in data
        assert len(data["status_history"]) == 3

        # Check status history format
        history_item = data["status_history"][0]
        assert "status" in history_item
        assert "feedback" in history_item
        assert "changed_at" in history_item

    def test_candidate_without_history(self):
        """Test serializer for candidate without status history."""
        candidate = CandidateFactory()

        serializer = CandidateStatusSerializer(candidate)
        data = serializer.data

        assert data["id"] == str(candidate.id)
        assert data["status_history"] == []


@pytest.mark.django_db
class TestCandidateListSerializer:
    """Test cases for CandidateListSerializer."""

    def test_serializer_output(self):
        """Test serializer output format."""
        candidate = CandidateFactory()

        serializer = CandidateListSerializer(candidate)
        data = serializer.data

        expected_fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "department",
            "years_of_experience",
            "current_status",
            "created_at",
        ]

        for field in expected_fields:
            assert field in data

        assert data["id"] == str(candidate.id)
        assert data["full_name"] == candidate.full_name
        assert data["department"] == candidate.department

    def test_multiple_candidates_serialization(self):
        """Test serializing multiple candidates."""
        candidates = CandidateFactory.create_batch(3)

        serializer = CandidateListSerializer(candidates, many=True)
        data = serializer.data

        assert len(data) == 3
        for item in data:
            assert "id" in item
            assert "full_name" in item
            assert "current_status" in item


@pytest.mark.django_db
class TestStatusUpdateSerializer:
    """Test cases for StatusUpdateSerializer."""

    def test_valid_status_update(self):
        """Test valid status update."""
        candidate = CandidateFactory(current_status=ApplicationStatus.SUBMITTED)

        data = {
            "status": ApplicationStatus.UNDER_REVIEW,
            "feedback": "Initial review completed",
        }

        serializer = StatusUpdateSerializer(candidate, data=data, partial=True)
        assert serializer.is_valid()

        updated_candidate = serializer.save()
        assert updated_candidate.current_status == ApplicationStatus.UNDER_REVIEW

        # Check that status history was created
        history = updated_candidate.status_history.first()
        assert history.status == ApplicationStatus.UNDER_REVIEW
        assert history.feedback == "Initial review completed"

    def test_invalid_status(self):
        """Test status update with invalid status."""
        candidate = CandidateFactory()

        data = {"status": "INVALID_STATUS", "feedback": "Some feedback"}

        serializer = StatusUpdateSerializer(candidate, data=data, partial=True)
        assert not serializer.is_valid()
        assert "status" in serializer.errors

    def test_status_update_without_feedback(self):
        """Test status update without feedback."""
        candidate = CandidateFactory(current_status=ApplicationStatus.SUBMITTED)

        data = {"status": ApplicationStatus.UNDER_REVIEW}

        serializer = StatusUpdateSerializer(candidate, data=data, partial=True)
        assert serializer.is_valid()

        updated_candidate = serializer.save()
        assert updated_candidate.current_status == ApplicationStatus.UNDER_REVIEW

        # Check that status history was created without feedback
        history = updated_candidate.status_history.first()
        assert history.status == ApplicationStatus.UNDER_REVIEW
        assert history.feedback is None or history.feedback == ""

    def test_no_duplicate_status_update(self):
        """Test that updating to the same status still creates history."""
        candidate = CandidateFactory(current_status=ApplicationStatus.UNDER_REVIEW)

        data = {
            "status": ApplicationStatus.UNDER_REVIEW,
            "feedback": "Additional review notes",
        }

        serializer = StatusUpdateSerializer(candidate, data=data, partial=True)
        assert serializer.is_valid()

        updated_candidate = serializer.save()
        assert updated_candidate.current_status == ApplicationStatus.UNDER_REVIEW

        # Should still create a new history entry
        history = updated_candidate.status_history.first()
        assert history.feedback == "Additional review notes"
