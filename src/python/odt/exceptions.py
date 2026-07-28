"""
ODT format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class OdtError(FormatFactoryError):
    """Base exception for all odt format errors."""


class OdtParseError(OdtError):
    """Raised when a odt file cannot be parsed."""


class OdtWriteError(OdtError):
    """Raised when a odt file cannot be written."""


class OdtInvalidContainerError(OdtParseError):
    """Raised when the ZIP container is invalid or missing required entries."""


class OdtSizeError(OdtParseError):
    """Raised when the file or decompressed content exceeds size limits."""
