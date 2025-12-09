"""
Compatibility shim: authentication exceptions are now split between users and tokens.

Import from `api.core.users.exceptions` and `api.core.tokens.exceptions` and re-export
to maintain backward compatibility while migrating.
"""

from truapi.core.tokens.exceptions import InvalidTokenError, TokenExpiredError
from truapi.core.users.exceptions import AuthenticationError, InvalidCredentialsError

__all__ = [
    "AuthenticationError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "TokenExpiredError",
]
