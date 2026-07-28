"""NRRD exception hierarchy."""

from format_factory.core import FormatFactoryError, FormatParseError, FormatWriteError


class NrrdError(FormatFactoryError):
    """Base exception for NRRD operations."""


class NrrdParseError(FormatParseError, NrrdError):
    """Raised for malformed, unsafe, or unsupported input."""


class NrrdWriteError(FormatWriteError, NrrdError):
    """Raised when a document cannot be serialized."""


class NrrdValidationError(NrrdError):
    """Raised when a document violates its selected profile."""
