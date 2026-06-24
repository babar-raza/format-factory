"""
NDJSON format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class NdjsonError(FormatFactoryError):
    """Base exception for all ndjson format errors."""


class NdjsonParseError(NdjsonError):
    """Raised when a ndjson file cannot be parsed."""


class NdjsonWriteError(NdjsonError):
    """Raised when a ndjson file cannot be written."""
