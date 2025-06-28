"""
Admin configuration for candidates app.
"""

from django.contrib import admin

from .models import Candidate, StatusHistory


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    """Admin interface for Candidate model."""

    list_display = [
        "full_name",
        "email",
        "department",
        "current_status",
        "years_of_experience",
        "created_at",
    ]
    list_filter = ["department", "current_status", "created_at"]
    search_fields = ["full_name", "email", "phone"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Personal Information",
            {"fields": ("id", "full_name", "email", "phone", "date_of_birth")},
        ),
        (
            "Professional Information",
            {"fields": ("years_of_experience", "department", "resume")},
        ),
        ("Application Status", {"fields": ("current_status",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    """Admin interface for StatusHistory model."""

    list_display = ["candidate", "status", "changed_at", "admin_info"]
    list_filter = ["status", "changed_at"]
    search_fields = ["candidate__full_name", "candidate__email"]
    readonly_fields = ["changed_at"]
    ordering = ["-changed_at"]
