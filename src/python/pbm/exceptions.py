"""
PBM format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class PbmError(FormatFactoryError):
    """Base exception for all pbm format errors."""


class PbmParseError(PbmError):
    """Raised when a pbm file cannot be parsed."""


class PbmWriteError(PbmError):
    """Raised when a pbm file cannot be written."""


class PbmInvalidMagicError(PbmParseError):
    """Raised when file does not start with P1 or P4."""


class PbmInvalidHeaderError(PbmParseError):
    """Raised when header fields are invalid."""


class PbmSizeError(PbmParseError):
    """Raised when file or image dimensions exceed limits."""


class PbmDecodeError(PbmParseError):
    """Raised when pixel data is malformed."""
