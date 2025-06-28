"""
Candidate models for the HR system.
"""

import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Department(models.TextChoices):
    """Department choices enum."""

    IT = "IT", "IT"
    HR = "HR", "HR"
    FINANCE = "Finance", "Finance"


class ApplicationStatus(models.TextChoices):
    """Application status choices enum."""

    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    INTERVIEW_SCHEDULED = "interview_scheduled", "Interview Scheduled"
    REJECTED = "rejected", "Rejected"
    ACCEPTED = "accepted", "Accepted"


class Candidate(models.Model):
    """Candidate model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    years_of_experience = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    department = models.CharField(max_length=20, choices=Department.choices)

    # Resume file information
    resume_file_id = models.CharField(
        max_length=255, help_text="File ID from upload endpoint"
    )
    resume_filename = models.CharField(max_length=255)
    resume_url = models.URLField(help_text="Permanent resume file URL")

    # Status tracking
    current_status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.SUBMITTED,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "candidates"
        indexes = [
            models.Index(fields=["department"]),
            models.Index(fields=["current_status"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.department}"

    def clean(self):
        """Custom validation."""
        super().clean()

        # Validate email uniqueness (case-insensitive)
        if self.email:
            existing = Candidate.objects.filter(email__iexact=self.email).exclude(
                pk=self.pk
            )
            if existing.exists():
                raise ValidationError(
                    {"email": "A candidate with this email already exists."}
                )


class StatusHistory(models.Model):
    """Track status changes for candidates."""

    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name="status_history"
    )
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices)
    feedback = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    admin_info = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "candidate_status_history"
        indexes = [
            models.Index(fields=["candidate", "-changed_at"]),
        ]
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.candidate.full_name} - {self.status} - {self.changed_at}"
