"""
ZST format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class ZstError(FormatFactoryError):
    """Base exception for all zst format errors."""


class ZstParseError(ZstError):
    """Raised when a zst file cannot be parsed."""


class ZstWriteError(ZstError):
    """Raised when a zst file cannot be written."""


class ZstInvalidFrameError(ZstParseError):
    """Raised when input is not a valid Zstandard frame."""


class ZstDecompressionError(ZstParseError):
    """Raised when decompression fails."""


class ZstFileNotFoundError(ZstParseError):
    """Raised when a ZST file does not exist."""


class ZstReadError(ZstParseError):
    """Raised when a ZST file cannot be read."""


class ZstDecompressError(ZstParseError):
    """Raised when decompression of a ZST file fails."""
