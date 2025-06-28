"""
Views for candidate management API.
"""

import logging

from django.http import Http404, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, status
from rest_framework.response import Response

from common.permissions import IsAdminHeaderPermission

from .models import Candidate
from .serializers import (
    CandidateListSerializer,
    CandidateRegistrationSerializer,
    CandidateStatusSerializer,
    StatusUpdateSerializer,
)

logger = logging.getLogger(__name__)


class CandidateRegistrationView(generics.CreateAPIView):
    """
    Register a new candidate.

    Public endpoint for candidate registration with resume upload.
    """

    serializer_class = CandidateRegistrationSerializer

    @extend_schema(
        summary="Register new candidate",
        description="Register a new candidate with personal details and resume upload",
        responses={201: CandidateRegistrationSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            candidate = serializer.save()
            logger.info(f"Candidate registered: {candidate.id}")
            return Response(
                {
                    "message": "Registration successful",
                    "candidate_id": str(candidate.id),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CandidateStatusView(generics.RetrieveAPIView):
    """
    Check application status for a candidate.

    Public endpoint to check application status using candidate ID.
    """

    queryset = Candidate.objects.all()
    serializer_class = CandidateStatusSerializer
    lookup_field = "id"

    @extend_schema(
        summary="Check application status",
        description="Get current application status and history for a candidate",
        responses={200: CandidateStatusSerializer},
    )
    def get(self, request, *args, **kwargs):
        try:
            candidate = self.get_object()
            serializer = self.get_serializer(candidate)
            return Response(serializer.data)
        except Http404:
            return Response(
                {"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AdminCandidateListView(generics.ListAPIView):
    """
    List all candidates with filtering and pagination.

    Admin-only endpoint to view all candidates with filters.
    """

    queryset = Candidate.objects.all()
    serializer_class = CandidateListSerializer
    permission_classes = [IsAdminHeaderPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["department", "current_status"]
    ordering_fields = ["created_at", "full_name", "years_of_experience"]
    ordering = ["-created_at"]

    @extend_schema(
        summary="List all candidates (Admin)",
        description="Get paginated list of all candidates with filtering options",
        parameters=[
            OpenApiParameter(
                name="X-ADMIN",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description='Admin header (must be "1")',
            ),
            OpenApiParameter(
                name="department",
                type=OpenApiTypes.STR,
                description="Filter by department (IT, HR, Finance)",
            ),
            OpenApiParameter(
                name="current_status",
                type=OpenApiTypes.STR,
                description="Filter by current status",
            ),
        ],
        responses={200: CandidateListSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminStatusUpdateView(generics.UpdateAPIView):
    """
    Update candidate status.

    Admin-only endpoint to update candidate application status.
    """

    queryset = Candidate.objects.all()
    serializer_class = StatusUpdateSerializer
    permission_classes = [IsAdminHeaderPermission]
    lookup_field = "id"

    @extend_schema(
        summary="Update candidate status (Admin)",
        description="Update candidate application status with optional feedback",
        parameters=[
            OpenApiParameter(
                name="X-ADMIN",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description='Admin header (must be "1")',
            ),
        ],
        responses={200: CandidateStatusSerializer},
    )
    def patch(self, request, *args, **kwargs):
        try:
            candidate = self.get_object()
            serializer = self.get_serializer(candidate, data=request.data, partial=True)

            if serializer.is_valid():
                updated_candidate = serializer.save()
                response_serializer = CandidateStatusSerializer(updated_candidate)
                return Response(response_serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Http404:
            return Response(
                {"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND
            )


class AdminResumeDownloadView(generics.RetrieveAPIView):
    """
    Download candidate resume.

    Admin-only endpoint to download candidate resume files.
    """

    queryset = Candidate.objects.all()
    permission_classes = [IsAdminHeaderPermission]
    lookup_field = "id"

    @extend_schema(
        summary="Download candidate resume (Admin)",
        description="Download resume file for a specific candidate",
        parameters=[
            OpenApiParameter(
                name="X-ADMIN",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description='Admin header (must be "1")',
            ),
        ],
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request, *args, **kwargs):
        try:
            candidate = self.get_object()

            if not candidate.resume_url or not candidate.resume_filename:
                return Response(
                    {"error": "No resume file found for this candidate"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # For both S3 and local storage, use the resume_url
            try:
                # Redirect to the file URL or serve it directly
                import os

                from django.conf import settings
                from django.http import HttpResponseRedirect

                if settings.USE_S3:
                    # For S3, redirect to the direct URL
                    return HttpResponseRedirect(candidate.resume_url)
                else:
                    # For local storage, serve the file directly
                    # The actual file is stored as resume_{file_id}.pdf
                    actual_filename = f"resume_{candidate.resume_file_id}.pdf"
                    file_path = os.path.join(
                        settings.MEDIA_ROOT,
                        "resumes",
                        str(candidate.id),
                        actual_filename,
                    )

                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            response = HttpResponse(
                                f.read(), content_type="application/pdf"
                            )
                            response[
                                "Content-Disposition"
                            ] = f'attachment; filename="{candidate.resume_filename}"'
                            logger.info(
                                f"Resume downloaded for candidate: {candidate.id}"
                            )
                            return response
                    else:
                        return Response(
                            {"error": f"Resume file not found at {file_path}"},
                            status=status.HTTP_404_NOT_FOUND,
                        )

            except Exception as e:
                logger.error(f"Error downloading resume for {candidate.id}: {str(e)}")
                return Response(
                    {"error": "Error accessing resume file"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Http404:
            return Response(
                {"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND
            )
