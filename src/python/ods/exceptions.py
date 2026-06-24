"""
ODS format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class OdsError(FormatFactoryError):
    """Base exception for all ods format errors."""


class OdsParseError(OdsError):
    """Raised when a ods file cannot be parsed."""


class OdsWriteError(OdsError):
    """Raised when a ods file cannot be written."""
