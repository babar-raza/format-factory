"""Exceptions for the nrrd codec."""

try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception  # type: ignore[misc,assignment]


class NrrdError(FormatFactoryError):
    """Base exception for nrrd operations."""


class NrrdParseError(NrrdError):
    """Raised when an nrrd file cannot be parsed."""


class NrrdWriteError(NrrdError):
    """Raised when an nrrd file cannot be written."""
