"""Jupyter Notebook exception hierarchy."""

from format_factory.core import FormatFactoryError


class IpynbError(FormatFactoryError):
    """Base exception for Jupyter Notebook operations."""


class IpynbParseError(IpynbError):
    """Raised when notebook input cannot be parsed safely."""


class IpynbWriteError(IpynbError):
    """Raised when a notebook cannot be serialized or written."""


class IpynbValidationError(IpynbError):
    """Raised when a notebook violates the selected profile."""


class IpynbExecutionError(IpynbError):
    """Raised when the opt-in execution adapter cannot run a notebook."""
