"""Exceptions for the safetensors codec."""

try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception  # type: ignore[misc,assignment]


class SafetensorsError(FormatFactoryError):
    """Base exception for safetensors operations."""


class SafetensorsParseError(SafetensorsError):
    """Raised when a safetensors file cannot be parsed."""


class SafetensorsWriteError(SafetensorsError):
    """Raised when a safetensors file cannot be written."""
