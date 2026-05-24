"""
format-factory-fods -- Python FOSS parser/writer for OpenDocument Flat Spreadsheet (FODS).

Public API:
    parse_fods(file_path)        -- streaming parser, never raises
    parse_fods_strict(file_path) -- raises FodsError subclasses on failure
    write_fods(workbook, path)   -- serialize neutral model workbook to FODS file
    workbook_to_xml(workbook)    -- serialize neutral model workbook to XML string
    workbook_stats(workbook)     -- return cell-level statistics dict (R57/R58)

License: Apache-2.0
Package: format-factory-fods v0.1.0
Gate history: Gates 1-10 PASSED (2026-05-08)
R46 MT6: write_fods / workbook_to_xml added (alpha-foss-preview write capability)
R57/R58: workbook_stats() exposed in public API
"""

from .parser import parse_fods, parse_fods_strict
from .writer import write_fods, workbook_to_xml
from .neutral_model import (
    workbook_stats,
    workbook_type_distribution,
    find_sheet_by_name,
    workbook_sheet_summary,
    workbook_empty_rows,
)
from .exceptions import FodsError, FodsInputError, FodsSizeError, FodsParseError
from .constants import FORMAT_ID, SPEC_VERSION, PACKAGE_VERSION, MAX_FILE_BYTES

__version__ = PACKAGE_VERSION
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_fods",
    "parse_fods_strict",
    "write_fods",
    "workbook_to_xml",
    "workbook_stats",
    "workbook_type_distribution",
    "find_sheet_by_name",
    "workbook_sheet_summary",
    "workbook_empty_rows",
    "FodsError",
    "FodsInputError",
    "FodsSizeError",
    "FodsParseError",
    "FORMAT_ID",
    "SPEC_VERSION",
    "PACKAGE_VERSION",
    "MAX_FILE_BYTES",
]
