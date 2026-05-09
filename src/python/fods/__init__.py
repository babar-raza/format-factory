"""
format-factory-fods -- Python FOSS parser for OpenDocument Flat Spreadsheet (FODS).

Public API:
    parse_fods(file_path)        -- streaming parser, never raises
    parse_fods_strict(file_path) -- raises FodsError subclasses on failure

License: Apache-2.0
Package: format-factory-fods v0.1.0
Gate history: Gates 1-10 PASSED (2026-05-08)
"""

from .parser import parse_fods, parse_fods_strict
from .exceptions import FodsError, FodsInputError, FodsSizeError, FodsParseError
from .constants import FORMAT_ID, SPEC_VERSION, PACKAGE_VERSION, MAX_FILE_BYTES

__version__ = PACKAGE_VERSION

__all__ = [
    "parse_fods",
    "parse_fods_strict",
    "FodsError",
    "FodsInputError",
    "FodsSizeError",
    "FodsParseError",
    "FORMAT_ID",
    "SPEC_VERSION",
    "PACKAGE_VERSION",
    "MAX_FILE_BYTES",
]
