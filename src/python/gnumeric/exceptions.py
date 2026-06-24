"""
Gnumeric format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class GnumericError(FormatFactoryError):
    """Base exception for all gnumeric format errors."""


class GnumericParseError(GnumericError):
    """Raised when a gnumeric file cannot be parsed."""


class GnumericWriteError(GnumericError):
    """Raised when a gnumeric file cannot be written."""
