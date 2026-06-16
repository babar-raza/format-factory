"""
exceptions.py -- Custom exceptions for format-factory-fods.

These exceptions are raised by the strict parse API (parse_fods_strict).
The standard parse_fods() function never raises; it returns an error dict.

License: Apache-2.0
Package: format-factory-fods v0.1.0
"""


class FodsError(ValueError):
    """Base exception for all format-factory-fods errors."""


class FodsInputError(FodsError):
    """Raised when the input file path is invalid.

    Conditions:
    - File does not exist.
    - Path exists but is not a regular file (e.g., a directory).
    """


class FodsSizeError(FodsError):
    """Raised when the input file exceeds the maximum allowed size.

    The size limit is constants.MAX_FILE_BYTES (100 MB).
    This guard prevents memory exhaustion when parsing enterprise FODS files.
    """


class FodsParseError(FodsError):
    """Raised when the FODS XML is structurally invalid or unparseable.

    Conditions:
    - xml.etree.ElementTree.ParseError (malformed XML).
    - Root element is not office:document.
    - office:body or office:spreadsheet element is absent.
    """
