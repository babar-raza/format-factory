"""
PGM format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class PgmError(FormatFactoryError):
    """Base exception for all pgm format errors."""


class PgmParseError(PgmError):
    """Raised when a pgm file cannot be parsed."""


class PgmWriteError(PgmError):
    """Raised when a pgm file cannot be written."""
