"""
Utility modules for the application.
"""

# Import all functions from email_utils to maintain backward compatibility
from .email_utils import (
    EmailData,
    generate_new_account_email,
    generate_password_reset_token,
    generate_reset_password_email,
    generate_test_email,
    render_email_template,
    send_email,
    verify_password_reset_token,
)

# Import HTTP client
from .http_client import HTTPClient, http_client

__all__ = [
    # Email utilities
    "EmailData",
    "generate_new_account_email", 
    "generate_password_reset_token",
    "generate_reset_password_email",
    "generate_test_email",
    "render_email_template",
    "send_email",
    "verify_password_reset_token",
    # HTTP client
    "HTTPClient",
    "http_client",
]
