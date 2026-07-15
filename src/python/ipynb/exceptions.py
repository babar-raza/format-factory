"""Exceptions for the ipynb codec."""

try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception  # type: ignore[misc,assignment]


class IpynbError(FormatFactoryError):
    """Base exception for ipynb operations."""


class IpynbParseError(IpynbError):
    """Raised when an ipynb file cannot be parsed."""


class IpynbWriteError(IpynbError):
    """Raised when an ipynb file cannot be written."""


class IpynbValidationError(IpynbError):
    """Raised when a notebook fails structural/schema validation.

    See ``ipynb.ipynb_codec.validate_notebook`` / ``validate_notebook_schema``.
    """
