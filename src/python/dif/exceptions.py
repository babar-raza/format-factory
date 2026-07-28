"""
DIF format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class DifError(FormatFactoryError):
    """Base exception for all dif format errors."""


class DifParseError(DifError):
    """Raised when a dif file cannot be parsed."""


class DifWriteError(DifError):
    """Raised when a dif file cannot be written."""


class DifInvalidFormatError(DifParseError):
    """Raised when file structure is not valid DIF."""


class DifSizeError(DifParseError):
    """Raised when file or data exceeds limits."""
