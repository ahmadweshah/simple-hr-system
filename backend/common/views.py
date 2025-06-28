"""
Views for file upload functionality.
"""

import logging

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.models import TemporaryFileUpload
from common.storage import FileUploadService
from common.utils import validate_file_size, validate_file_type

logger = logging.getLogger(__name__)


class FileUploadView(APIView):
    """
    Upload resume files and get temporary URLs.

    This endpoint allows users to upload resume files before registration.
    Returns a file ID that can be used in the registration process.
    """

    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Upload resume file",
        description="Upload a resume file (PDF or DOCX, max 5MB) and receive a file ID for registration",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Resume file (PDF or DOCX, max 5MB)",
                    }
                },
                "required": ["file"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Unique file identifier",
                    },
                    "filename": {"type": "string", "description": "Original filename"},
                    "url": {"type": "string", "description": "Temporary file URL"},
                    "expires_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "URL expiration time",
                    },
                    "message": {"type": "string", "description": "Success message"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "description": "Error message"}
                },
            },
        },
    )
    def post(self, request):
        """Upload a file and return file ID for later use."""
        try:
            # Check if file is provided
            if "file" not in request.FILES:
                return Response(
                    {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
                )

            uploaded_file = request.FILES["file"]

            # Validate file type
            try:
                allowed_types = [
                    "application/pdf",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ]
                validate_file_type(uploaded_file, allowed_types)
                validate_file_size(uploaded_file, max_size_mb=5)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # Upload file using storage service
            upload_service = FileUploadService()
            file_info = upload_service.upload_resume(uploaded_file)

            # Save temporary file record
            temp_file = TemporaryFileUpload.objects.create(
                file_id=file_info["file_id"],
                original_filename=uploaded_file.name,
                content_type=uploaded_file.content_type,
                file_size=uploaded_file.size,
                storage_info=file_info,
            )

            logger.info(f"File uploaded successfully: {file_info['file_id']}")

            return Response(
                {
                    "file_id": file_info["file_id"],
                    "filename": file_info["filename"],
                    "url": file_info["url"],
                    "expires_at": temp_file.expires_at.isoformat(),
                    "message": "File uploaded successfully. Use the file_id when registering.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            return Response(
                {"error": "File upload failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FileInfoView(APIView):
    """
    Get information about an uploaded file.

    This endpoint allows users to check the status of a previously uploaded file.
    """

    @extend_schema(
        summary="Get file information",
        description="Get information about a previously uploaded file using its file ID",
        parameters=[
            OpenApiParameter(
                name="file_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description="File ID returned from upload endpoint",
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string"},
                    "filename": {"type": "string"},
                    "content_type": {"type": "string"},
                    "file_size": {"type": "integer"},
                    "uploaded_at": {"type": "string", "format": "date-time"},
                    "expires_at": {"type": "string", "format": "date-time"},
                    "is_expired": {"type": "boolean"},
                    "is_used": {"type": "boolean"},
                },
            },
            404: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    )
    def get(self, request, file_id):
        """Get file information by file ID."""
        try:
            temp_file = TemporaryFileUpload.objects.get(file_id=file_id)

            return Response(
                {
                    "file_id": temp_file.file_id,
                    "filename": temp_file.original_filename,
                    "content_type": temp_file.content_type,
                    "file_size": temp_file.file_size,
                    "uploaded_at": temp_file.created_at.isoformat(),
                    "expires_at": temp_file.expires_at.isoformat(),
                    "is_expired": temp_file.is_expired(),
                    "is_used": temp_file.is_used,
                },
                status=status.HTTP_200_OK,
            )

        except TemporaryFileUpload.DoesNotExist:
            return Response(
                {"error": "File not found"}, status=status.HTTP_404_NOT_FOUND
            )
