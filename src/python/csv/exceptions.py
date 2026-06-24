"""
CSV format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class CsvError(FormatFactoryError):
    """Base exception for all csv format errors."""


class CsvParseError(CsvError):
    """Raised when a csv file cannot be parsed."""


class CsvWriteError(CsvError):
    """Raised when a csv file cannot be written."""
