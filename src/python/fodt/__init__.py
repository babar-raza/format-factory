"""
format-factory-fodt -- Python FOSS parser/writer for OpenDocument Flat Text (FODT).

Public API:
    parse_fodt(file_path)        -- streaming parser, never raises
    parse_fodt_strict(file_path) -- raises FodtError subclasses on failure
    write_fodt(document, path)   -- serialize neutral model document to FODT file
    document_to_xml(document)    -- serialize neutral model document to XML string
    document_stats(document)     -- return document-level statistics dict (R57/R58)
    document_heading_outline(document) -- ordered heading list for TOC (R59)
    document_text_content(document)    -- full text extraction as single string (R59)

License: Apache-2.0
Package: format-factory-fodt v0.1.0
Gate history: Gates 1-9 PASSED (2026-05-08); Gate 10 Phase 4 code-complete (2026-05-09)
R46 MT6: write_fodt / document_to_xml added (alpha-foss-preview write capability)
R57/R58: document_stats() exposed in public API
"""

from .parser import parse_fodt, parse_fodt_strict
from .writer import write_fodt, document_to_xml
from .neutral_model import (
    document_stats,
    document_heading_outline,
    document_text_content,
    document_word_count,
    document_table_summary,
)
from .exceptions import FodtError, FodtInputError, FodtSizeError, FodtParseError
from .constants import FORMAT_ID, SPEC_VERSION, PACKAGE_VERSION, MAX_FILE_BYTES

__version__ = PACKAGE_VERSION
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_fodt",
    "parse_fodt_strict",
    "write_fodt",
    "document_to_xml",
    "document_stats",
    "document_heading_outline",
    "document_text_content",
    "document_word_count",
    "document_table_summary",
    "FodtError",
    "FodtInputError",
    "FodtSizeError",
    "FodtParseError",
    "FORMAT_ID",
    "SPEC_VERSION",
    "PACKAGE_VERSION",
    "MAX_FILE_BYTES",
]
