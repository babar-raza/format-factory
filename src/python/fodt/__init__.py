"""
format-factory-fodt -- Python FOSS parser for OpenDocument Flat Text (FODT).

Public API:
    parse_fodt(file_path)        -- streaming parser, never raises
    parse_fodt_strict(file_path) -- raises FodtError subclasses on failure

License: Apache-2.0
Package: format-factory-fodt v0.1.0
Gate history: Gates 1-9 PASSED (2026-05-08); Gate 10 Phase 4 code-complete (2026-05-09)
"""

from .parser import parse_fodt, parse_fodt_strict
from .exceptions import FodtError, FodtInputError, FodtSizeError, FodtParseError
from .constants import FORMAT_ID, SPEC_VERSION, PACKAGE_VERSION, MAX_FILE_BYTES

__version__ = PACKAGE_VERSION
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_fodt",
    "parse_fodt_strict",
    "FodtError",
    "FodtInputError",
    "FodtSizeError",
    "FodtParseError",
    "FORMAT_ID",
    "SPEC_VERSION",
    "PACKAGE_VERSION",
    "MAX_FILE_BYTES",
]
