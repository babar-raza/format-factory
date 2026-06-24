"""
ZST format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class ZstError(FormatFactoryError):
    """Base exception for all zst format errors."""


class ZstParseError(ZstError):
    """Raised when a zst file cannot be parsed."""


class ZstWriteError(ZstError):
    """Raised when a zst file cannot be written."""
