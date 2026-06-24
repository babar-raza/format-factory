"""
FODP format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class FodpError(FormatFactoryError):
    """Base exception for all fodp format errors."""


class FodpParseError(FodpError):
    """Raised when a fodp file cannot be parsed."""


class FodpWriteError(FodpError):
    """Raised when a fodp file cannot be written."""
