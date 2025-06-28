"""
File storage service for handling uploads to S3 or local storage.
"""

import logging
import os
import uuid

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


class FileUploadService:
    """Service for handling file uploads with S3 and local storage support."""

    def __init__(self):
        self.use_s3 = getattr(settings, "USE_S3", False)
        if self.use_s3:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    def upload_resume(self, file, filename=None):
        """
        Upload resume file and return URL.

        Args:
            file: Uploaded file object
            filename: Optional custom filename

        Returns:
            dict: Contains 'url', 'file_id', and 'filename'
        """
        try:
            # Generate unique file ID and filename
            file_id = str(uuid.uuid4())
            if not filename:
                file_extension = os.path.splitext(file.name)[1]
                filename = f"resume_{file_id}{file_extension}"

            if self.use_s3:
                return self._upload_to_s3(file, file_id, filename)
            else:
                return self._upload_to_local(file, file_id, filename)

        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise Exception(f"File upload failed: {str(e)}")

    def _upload_to_s3(self, file, file_id, filename):
        """Upload file to S3 and return signed URL."""
        try:
            # Construct S3 key
            s3_key = f"temp_resumes/{file_id}/{filename}"

            # Upload to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": file.content_type or "application/octet-stream",
                    "Metadata": {"original_name": file.name, "file_id": file_id},
                },
            )

            # Generate signed URL for access (valid for 1 hour)
            signed_url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=3600,
            )

            logger.info(f"File uploaded to S3: {s3_key}")

            return {
                "url": signed_url,
                "file_id": file_id,
                "filename": filename,
                "s3_key": s3_key,
                "storage_type": "s3",
            }

        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise Exception(f"S3 upload failed: {str(e)}")

    def _upload_to_local(self, file, file_id, filename):
        """Upload file to local storage and return URL."""
        try:
            # Construct local path
            local_path = f"temp_resumes/{file_id}/{filename}"

            # Save file using Django's default storage
            saved_path = default_storage.save(local_path, ContentFile(file.read()))

            # Generate URL
            file_url = default_storage.url(saved_path)

            # Make it a full URL if it's relative
            if file_url.startswith("/"):
                # Use Django request to build full URL or fallback
                from django.conf import settings

                if hasattr(settings, "ALLOWED_HOSTS") and settings.ALLOWED_HOSTS:
                    # Use the first allowed host, or localhost for development
                    host = (
                        settings.ALLOWED_HOSTS[0]
                        if settings.ALLOWED_HOSTS[0] != "*"
                        else "localhost:8003"
                    )
                    file_url = f"http://{host}{file_url}"
                else:
                    # Fallback to localhost for development
                    file_url = f"http://localhost:8003{file_url}"

            logger.info(f"File uploaded locally: {saved_path}")

            return {
                "url": file_url,
                "file_id": file_id,
                "filename": filename,
                "local_path": saved_path,
                "storage_type": "local",
            }

        except Exception as e:
            logger.error(f"Local upload error: {str(e)}")
            raise Exception(f"Local upload failed: {str(e)}")

    def move_temp_file_to_permanent(self, file_info, candidate_id):
        """
        Move temporary uploaded file to permanent location.

        Args:
            file_info: File info dict from upload_resume
            candidate_id: UUID of the candidate

        Returns:
            str: Permanent file URL/path
        """
        try:
            if self.use_s3:
                return self._move_s3_file_to_permanent(file_info, candidate_id)
            else:
                return self._move_local_file_to_permanent(file_info, candidate_id)

        except Exception as e:
            logger.error(f"Error moving file to permanent location: {str(e)}")
            raise Exception(f"Failed to finalize file upload: {str(e)}")

    def _move_s3_file_to_permanent(self, file_info, candidate_id):
        """Move S3 file from temp to permanent location."""
        try:
            old_key = file_info["s3_key"]
            new_key = f"resumes/{candidate_id}/{file_info['filename']}"

            # Copy object to new location
            copy_source = {"Bucket": self.bucket_name, "Key": old_key}
            self.s3_client.copy_object(
                CopySource=copy_source, Bucket=self.bucket_name, Key=new_key
            )

            # Delete old object
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=old_key)

            # Return permanent URL
            permanent_url = f"https://{self.bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{new_key}"

            logger.info(f"File moved to permanent S3 location: {new_key}")
            return permanent_url

        except ClientError as e:
            logger.error(f"S3 move error: {str(e)}")
            raise Exception(f"Failed to move S3 file: {str(e)}")

    def _move_local_file_to_permanent(self, file_info, candidate_id):
        """Move local file from temp to permanent location."""
        try:
            old_path = file_info["local_path"]
            new_path = f"resumes/{candidate_id}/{file_info['filename']}"

            # Read old file
            old_file_content = default_storage.open(old_path).read()

            # Save to new location
            permanent_path = default_storage.save(
                new_path, ContentFile(old_file_content)
            )

            # Delete old file
            default_storage.delete(old_path)

            # Return permanent URL
            permanent_url = default_storage.url(permanent_path)

            logger.info(f"File moved to permanent local location: {permanent_path}")
            return permanent_url

        except Exception as e:
            logger.error(f"Local move error: {str(e)}")
            raise Exception(f"Failed to move local file: {str(e)}")

    def delete_temp_file(self, file_info):
        """Delete temporary uploaded file."""
        try:
            if file_info["storage_type"] == "s3":
                self.s3_client.delete_object(
                    Bucket=self.bucket_name, Key=file_info["s3_key"]
                )
            else:
                default_storage.delete(file_info["local_path"])

            logger.info(f"Temporary file deleted: {file_info['file_id']}")

        except Exception as e:
            logger.error(f"Error deleting temp file: {str(e)}")
            # Don't raise exception for cleanup errors
