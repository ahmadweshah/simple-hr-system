"""
Custom middleware for the HR system.
"""

import logging

logger = logging.getLogger(__name__)


class AdminHeaderMiddleware:
    """
    Middleware to check for admin header and add it to request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for admin header
        request.is_admin = request.headers.get("X-ADMIN") == "1"

        # Log admin access
        if request.is_admin:
            logger.info(
                f"Admin access: {request.method} {request.path} from {request.META.get('REMOTE_ADDR')}"
            )

        response = self.get_response(request)
        return response
