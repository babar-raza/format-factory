"""
Format Factory shared infrastructure.

Provides the shared exception hierarchy for all format packages.
"""
from ._shared_exceptions import FormatFactoryError, ParseError, WriteError, ValidationError, SizeLimitError

__all__ = [
    "FormatFactoryError",
    "ParseError",
    "WriteError",
    "ValidationError",
    "SizeLimitError",
]
