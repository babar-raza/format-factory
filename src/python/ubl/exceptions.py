"""Exceptions for the ubl codec."""

try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception  # type: ignore[misc,assignment]


class UblError(FormatFactoryError):
    """Base exception for ubl operations."""


class UblParseError(UblError):
    """Raised when a UBL file cannot be parsed."""


class UblWriteError(UblError):
    """Raised when a UBL file cannot be written."""
