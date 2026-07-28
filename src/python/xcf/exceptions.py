"""
XCF format exceptions.

All exceptions inherit from FormatFactoryError via _shared for consistent
error handling across all format packages.
"""
try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class XcfError(FormatFactoryError):
    """Base exception for all xcf format errors."""


class XcfParseError(XcfError):
    """Raised when a xcf file cannot be parsed."""


class XcfWriteError(XcfError):
    """Raised when a xcf file cannot be written."""


class XcfInvalidMagicError(XcfParseError):
    """Raised when the file magic is not 'gimp xcf '."""


class XcfInvalidHeaderError(XcfParseError):
    """Raised when header fields are invalid."""


class XcfSizeError(XcfParseError):
    """Raised when file or image dimensions exceed limits."""
