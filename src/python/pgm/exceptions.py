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


class PgmInvalidMagicError(PgmParseError):
    """Raised when file does not start with P2 or P5."""


class PgmInvalidHeaderError(PgmParseError):
    """Raised when header fields are invalid."""


class PgmSizeError(PgmParseError):
    """Raised when file or image dimensions exceed limits."""


class PgmDecodeError(PgmParseError):
    """Raised when pixel data is malformed."""
