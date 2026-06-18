"""
Format Factory shared infrastructure.

Provides base classes and shared exception hierarchy for all format packages.
"""
from ._shared_exceptions import FormatFactoryError, ParseError, WriteError, ValidationError, SizeLimitError
from ._base_parser import BaseParser
from ._base_codec import BaseCodec

__all__ = [
    "FormatFactoryError",
    "ParseError",
    "WriteError",
    "ValidationError",
    "SizeLimitError",
    "BaseParser",
    "BaseCodec",
]
