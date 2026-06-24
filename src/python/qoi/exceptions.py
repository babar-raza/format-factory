"""
QOI format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class QoiError(FormatFactoryError):
    """Base exception for all qoi format errors."""


class QoiParseError(QoiError):
    """Raised when a qoi file cannot be parsed."""


class QoiWriteError(QoiError):
    """Raised when a qoi file cannot be written."""
