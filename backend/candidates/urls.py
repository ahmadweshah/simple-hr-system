"""
URL configuration for candidates app.
"""

from django.urls import path

from . import views

urlpatterns = [
    # Public endpoints
    path(
        "candidates/",
        views.CandidateRegistrationView.as_view(),
        name="candidate-registration",
    ),
    path(
        "candidates/<uuid:id>/status/",
        views.CandidateStatusView.as_view(),
        name="candidate-status",
    ),
    # Admin endpoints
    path(
        "admin/candidates/",
        views.AdminCandidateListView.as_view(),
        name="admin-candidate-list",
    ),
    path(
        "admin/candidates/<uuid:id>/status/",
        views.AdminStatusUpdateView.as_view(),
        name="admin-status-update",
    ),
    path(
        "admin/candidates/<uuid:id>/resume/",
        views.AdminResumeDownloadView.as_view(),
        name="admin-resume-download",
    ),
]
