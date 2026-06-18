"""
Base exception hierarchy shared across all Format Factory format packages.

Every format-specific exception class must inherit from FormatFactoryError.

Usage:
    from src.python._shared._shared_exceptions import ParseError

    class FodsParseError(ParseError):
        pass
"""


class FormatFactoryError(Exception):
    """Base class for all Format Factory errors."""


class ParseError(FormatFactoryError):
    """Raised when a file cannot be parsed."""


class WriteError(FormatFactoryError):
    """Raised when a file cannot be written."""


class ValidationError(FormatFactoryError):
    """Raised when a loaded document fails validation."""


class SizeLimitError(FormatFactoryError):
    """Raised when a file or document exceeds a configured size limit."""
