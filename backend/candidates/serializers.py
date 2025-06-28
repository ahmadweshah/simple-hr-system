"""
Serializers for candidate API endpoints.
"""

import logging

from rest_framework import serializers

from common.models import TemporaryFileUpload
from common.storage import FileUploadService

from .models import ApplicationStatus, Candidate, StatusHistory

logger = logging.getLogger(__name__)


class CandidateRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for candidate registration."""

    file_id = serializers.CharField(
        write_only=True, help_text="File ID from the upload endpoint"
    )

    class Meta:
        model = Candidate
        fields = [
            "full_name",
            "email",
            "phone",
            "date_of_birth",
            "years_of_experience",
            "department",
            "file_id",
        ]

    def validate_email(self, value):
        """Validate email uniqueness (case-insensitive)."""
        if Candidate.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A candidate with this email already exists."
            )
        return value.lower()

    def validate_phone(self, value):
        """Validate phone uniqueness."""
        if Candidate.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                "A candidate with this phone number already exists."
            )
        return value

    def validate_file_id(self, value):
        """Validate that the file_id exists and is not expired."""
        try:
            temp_file = TemporaryFileUpload.objects.get(file_id=value)

            if temp_file.is_expired():
                raise serializers.ValidationError(
                    "File upload has expired. Please upload the file again."
                )

            if temp_file.is_used:
                raise serializers.ValidationError(
                    "This file has already been used for another registration."
                )

            return value

        except TemporaryFileUpload.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid file ID. Please upload the file first."
            )

    def validate(self, data):
        """Cross-field validation."""
        from datetime import date

        # Validate that years of experience doesn't exceed age
        if "date_of_birth" in data and "years_of_experience" in data:
            birth_date = data["date_of_birth"]
            if isinstance(birth_date, str):
                # Parse string date
                from datetime import datetime

                birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()

            today = date.today()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

            # Assuming minimum working age is 16
            max_possible_experience = max(0, age - 16)

            if data["years_of_experience"] > max_possible_experience:
                raise serializers.ValidationError(
                    {
                        "years_of_experience": f"Years of experience ({data['years_of_experience']}) cannot exceed {max_possible_experience} years based on your age ({age} years old)."
                    }
                )

        return data

    def create(self, validated_data):
        """Create candidate and handle file processing."""
        file_id = validated_data.pop("file_id")

        # Get the temporary file upload record
        temp_file = TemporaryFileUpload.objects.get(file_id=file_id)

        # Create the candidate first
        candidate = Candidate.objects.create(**validated_data)

        try:
            # Move file to permanent location
            file_service = FileUploadService()
            storage_info = temp_file.get_storage_info()
            permanent_url = file_service.move_temp_file_to_permanent(
                storage_info, candidate.id
            )

            # Update candidate with file information
            candidate.resume_file_id = file_id
            candidate.resume_filename = temp_file.original_filename
            candidate.resume_url = permanent_url
            candidate.save()

            # Mark temporary file as used
            temp_file.mark_as_used()

        except Exception as e:
            # If file processing fails, delete the candidate and re-raise
            candidate.delete()
            logger.error(
                f"Failed to process file for candidate {candidate.email}: {str(e)}"
            )
            raise serializers.ValidationError(f"File processing failed: {str(e)}")

        # Create initial status history
        StatusHistory.objects.create(
            candidate=candidate,
            status=ApplicationStatus.SUBMITTED,
            feedback="Application submitted successfully",
        )

        logger.info(
            f"New candidate registered: {candidate.full_name} ({candidate.email})"
        )
        return candidate


class StatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for status history."""

    class Meta:
        model = StatusHistory
        fields = ["status", "feedback", "changed_at", "admin_info"]


class CandidateStatusSerializer(serializers.ModelSerializer):
    """Serializer for candidate status response."""

    status_history = StatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Candidate
        fields = [
            "id",
            "full_name",
            "current_status",
            "created_at",
            "updated_at",
            "status_history",
        ]


class CandidateListSerializer(serializers.ModelSerializer):
    """Serializer for candidate list (admin view)."""

    class Meta:
        model = Candidate
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "date_of_birth",
            "years_of_experience",
            "department",
            "current_status",
            "created_at",
            "updated_at",
        ]


class StatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating candidate status."""

    status = serializers.ChoiceField(choices=ApplicationStatus.choices)
    feedback = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    def update(self, instance, validated_data):
        """Update candidate status and create history entry."""
        new_status = validated_data["status"]
        feedback = validated_data.get("feedback", "")

        # Update candidate status
        instance.current_status = new_status
        instance.save()

        # Create status history entry
        StatusHistory.objects.create(
            candidate=instance,
            status=new_status,
            feedback=feedback,
            admin_info="Updated via API",
        )

        logger.info(f"Status updated for {instance.full_name}: {new_status}")

        # Mock notification (in real app, this could be email/SMS)
        print(
            f"NOTIFICATION: Dear {instance.full_name}, your application status has been updated to: {new_status}"
        )
        if feedback:
            print(f"Feedback: {feedback}")

        return instance
