"""
exceptions.py -- Custom exceptions for format-factory-fodt.

These exceptions are raised by the strict parse API (parse_fodt_strict).
The standard parse_fodt() function never raises; it returns an error dict.

License: Apache-2.0
Package: format-factory-fodt v0.1.0
"""

try:
    from _shared._shared_exceptions import FormatFactoryError
except ImportError:
    FormatFactoryError = Exception


class FodtError(FormatFactoryError):
    """Base exception for all format-factory-fodt errors."""


class FodtInputError(FodtError):
    """Raised when the input file path is invalid.

    Conditions:
    - File does not exist.
    - Path exists but is not a regular file (e.g., a directory).
    """


class FodtSizeError(FodtError):
    """Raised when the input file exceeds the maximum allowed size.

    The size limit is constants.MAX_FILE_BYTES (100 MB).
    This guard prevents memory exhaustion when parsing large FODT files.
    """


class FodtParseError(FodtError):
    """Raised when the FODT XML is structurally invalid or unparseable.

    Conditions:
    - xml.etree.ElementTree.ParseError (malformed XML).
    - Root element is not office:document.
    - office:body or office:text element is absent.
    """
