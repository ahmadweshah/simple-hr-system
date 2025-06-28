"""
Test permissions for the common app.
"""

from rest_framework.test import APIRequestFactory

from common.permissions import IsAdminHeaderPermission


class TestIsAdminHeaderPermission:
    """Test cases for IsAdminHeaderPermission."""

    def setup_method(self):
        """Set up test request factory."""
        self.factory = APIRequestFactory()
        self.permission = IsAdminHeaderPermission()

    def test_permission_with_valid_admin_header(self):
        """Test permission grants access with valid admin header."""
        request = self.factory.get("/", HTTP_X_ADMIN="1")

        has_permission = self.permission.has_permission(request, None)
        assert has_permission is True

    def test_permission_without_admin_header(self):
        """Test permission denies access without admin header."""
        request = self.factory.get("/")

        has_permission = self.permission.has_permission(request, None)
        assert has_permission is False

    def test_permission_with_invalid_admin_header_value(self):
        """Test permission denies access with invalid admin header value."""
        request = self.factory.get("/", HTTP_X_ADMIN="0")

        has_permission = self.permission.has_permission(request, None)
        assert has_permission is False

        # Test with other invalid values
        invalid_values = ["false", "no", "admin", "2", ""]
        for value in invalid_values:
            request = self.factory.get("/", HTTP_X_ADMIN=value)
            has_permission = self.permission.has_permission(request, None)
            assert has_permission is False

    def test_permission_with_case_sensitive_header(self):
        """Test that permission is case sensitive for header value."""
        # The header name should be case insensitive, but value should be case sensitive
        request = self.factory.get("/", HTTP_X_ADMIN="1")
        has_permission = self.permission.has_permission(request, None)
        assert has_permission is True

        # Test with wrong case for value
        request = self.factory.get("/", HTTP_X_ADMIN="TRUE")
        has_permission = self.permission.has_permission(request, None)
        assert has_permission is False

    def test_permission_with_different_request_methods(self):
        """Test permission works with different HTTP methods."""
        methods = ["get", "post", "put", "patch", "delete"]

        for method in methods:
            request = getattr(self.factory, method)("/", HTTP_X_ADMIN="1")
            has_permission = self.permission.has_permission(request, None)
            assert has_permission is True

            # Test without header for each method
            request = getattr(self.factory, method)("/")
            has_permission = self.permission.has_permission(request, None)
            assert has_permission is False

    def test_permission_object_level(self):
        """Test that object-level permission is not implemented."""
        request = self.factory.get("/", HTTP_X_ADMIN="1")

        # has_object_permission should return True by default
        # since we only check at the view level
        has_object_permission = self.permission.has_object_permission(
            request, None, None
        )
        assert has_object_permission is True

    def test_permission_with_extra_headers(self):
        """Test permission works when other headers are present."""
        request = self.factory.get(
            "/",
            HTTP_X_ADMIN="1",
            HTTP_AUTHORIZATION="Bearer token",
            HTTP_CONTENT_TYPE="application/json",
        )

        has_permission = self.permission.has_permission(request, None)
        assert has_permission is True

    def test_permission_header_name_variations(self):
        """Test permission with different header name formats."""
        # Django converts HTTP_X_ADMIN to X-Admin in META
        request = self.factory.get("/")
        request.META["HTTP_X_ADMIN"] = "1"

        has_permission = self.permission.has_permission(request, None)
        assert has_permission is True

        # Test without the header
        request = self.factory.get("/")
        has_permission = self.permission.has_permission(request, None)
        assert has_permission is False
