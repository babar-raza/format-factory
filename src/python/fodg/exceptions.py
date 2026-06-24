"""
FODG format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class FodgError(FormatFactoryError):
    """Base exception for all fodg format errors."""


class FodgParseError(FodgError):
    """Raised when a fodg file cannot be parsed."""


class FodgWriteError(FodgError):
    """Raised when a fodg file cannot be written."""
