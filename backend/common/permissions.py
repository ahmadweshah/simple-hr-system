"""
Custom permissions for the HR system.
"""

from rest_framework import permissions


class IsAdminHeaderPermission(permissions.BasePermission):
    """
    Custom permission to only allow access to users with X-ADMIN=1 header.
    """

    def has_permission(self, request, view):
        return request.headers.get("X-ADMIN") == "1"
