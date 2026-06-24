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
