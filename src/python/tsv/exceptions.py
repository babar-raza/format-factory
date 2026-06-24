"""
TSV format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class TsvError(FormatFactoryError):
    """Base exception for all tsv format errors."""


class TsvParseError(TsvError):
    """Raised when a tsv file cannot be parsed."""


class TsvWriteError(TsvError):
    """Raised when a tsv file cannot be written."""
