"""
SYLK format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class SylkError(FormatFactoryError):
    """Base exception for all sylk format errors."""


class SylkParseError(SylkError):
    """Raised when a sylk file cannot be parsed."""


class SylkWriteError(SylkError):
    """Raised when a sylk file cannot be written."""
