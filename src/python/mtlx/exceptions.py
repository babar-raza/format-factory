"""Exceptions for the mtlx codec."""

try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception  # type: ignore[misc,assignment]


class MtlxError(FormatFactoryError):
    """Base exception for mtlx operations."""


class MtlxParseError(MtlxError):
    """Raised when a mtlx file cannot be parsed."""


class MtlxWriteError(MtlxError):
    """Raised when a mtlx file cannot be written."""
