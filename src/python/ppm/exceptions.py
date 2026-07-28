"""
PPM format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class PpmError(FormatFactoryError):
    """Base exception for all ppm format errors."""


class PpmParseError(PpmError):
    """Raised when a ppm file cannot be parsed."""


class PpmWriteError(PpmError):
    """Raised when a ppm file cannot be written."""


class PpmInvalidMagicError(PpmParseError):
    """Raised when file does not start with P3 or P6."""


class PpmInvalidHeaderError(PpmParseError):
    """Raised when header fields are invalid."""


class PpmSizeError(PpmParseError):
    """Raised when file or image dimensions exceed limits."""


class PpmDecodeError(PpmParseError):
    """Raised when pixel data is malformed."""
