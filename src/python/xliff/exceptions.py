"""Exceptions for the xliff codec."""

try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception  # type: ignore[misc,assignment]


class XliffError(FormatFactoryError):
    """Base exception for xliff operations."""


class XliffParseError(XliffError):
    """Raised when an xliff file cannot be parsed."""


class XliffWriteError(XliffError):
    """Raised when an xliff file cannot be written."""
