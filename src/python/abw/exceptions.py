"""
AbiWord format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class AbwError(FormatFactoryError):
    """Base exception for all abw format errors."""


class AbwParseError(AbwError):
    """Raised when a abw file cannot be parsed."""


class AbwWriteError(AbwError):
    """Raised when a abw file cannot be written."""
