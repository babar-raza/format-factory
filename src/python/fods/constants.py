"""
constants.py — FODS parser constants for format-factory-fods.

ODF namespace URIs, qualified element/attribute names, limits, and
format identity constants used across the FODS Python FOSS package.

ODF 1.3 spec citation:
  source: ODF 1.3 Part 3 (schema spec)
  source_hash: sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066
  shared_spec_facts:
    FACT-ODF-SHARED-001: ODF 1.3 is an OASIS Standard published 27 April 2021
    FACT-ODF-SHARED-005: ODF package is a ZIP file using STORED or DEFLATED compression
    FACT-ODF-SHARED-010: OpenFormula is defined in ODF 1.3 Part 4 for spreadsheet formula cells

License: Apache-2.0
Package: format-factory-fods v0.1.0
"""

# ---------------------------------------------------------------------------
# Format identity
# ---------------------------------------------------------------------------

FORMAT_ID: str = "fods"
SPEC_VERSION: str = "ODF 1.3"
PACKAGE_VERSION: str = "0.1.0"

# ---------------------------------------------------------------------------
# MIME type (IR-FODS-001, IR-FODS-002 -- FFODS-002)
# ---------------------------------------------------------------------------

EXPECTED_MIMETYPE: str = (
    "application/vnd.oasis.opendocument.spreadsheet-flat-xml"
)

# ---------------------------------------------------------------------------
# File size guard (IR-FODS-003 -- FFODS-009)
# ---------------------------------------------------------------------------

MAX_FILE_BYTES: int = 100 * 1024 * 1024  # 100 MB

# ---------------------------------------------------------------------------
# Expansion caps -- prevent large memory allocations from repeat attributes
# (IR-FODS-010, IR-FODS-011)
# ---------------------------------------------------------------------------

MAX_EXPAND_REPEAT: int = 128

# ---------------------------------------------------------------------------
# ODF 1.3 XML namespace URIs (ODF 1.3 section 3.1.2)
# ---------------------------------------------------------------------------

NS_OFFICE: str = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
NS_TABLE: str  = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
NS_TEXT: str   = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
NS_DRAW: str   = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

# ---------------------------------------------------------------------------
# Qualified element names (Clark notation: {uri}localname)
# ---------------------------------------------------------------------------

QN_DOCUMENT:    str = f"{{{NS_OFFICE}}}document"  # FACT-FODS-001: root element is office:document
QN_BODY:        str = f"{{{NS_OFFICE}}}body"
QN_SPREADSHEET: str = f"{{{NS_OFFICE}}}spreadsheet"
QN_SCRIPTS:     str = f"{{{NS_OFFICE}}}scripts"
QN_AUTO_STYLES: str = f"{{{NS_OFFICE}}}automatic-styles"
QN_STYLES:      str = f"{{{NS_OFFICE}}}styles"
QN_TABLE:       str = f"{{{NS_TABLE}}}table"
QN_TABLE_COL:   str = f"{{{NS_TABLE}}}table-column"
QN_ROW:         str = f"{{{NS_TABLE}}}table-row"
QN_CELL:        str = f"{{{NS_TABLE}}}table-cell"
QN_COVERED:     str = f"{{{NS_TABLE}}}covered-table-cell"
QN_TEXT_P:      str = f"{{{NS_TEXT}}}p"
QN_TEXT_SPAN:   str = f"{{{NS_TEXT}}}span"
QN_DRAW_FRAME:  str = f"{{{NS_DRAW}}}frame"

# ---------------------------------------------------------------------------
# Qualified attribute names
# ---------------------------------------------------------------------------

ATTR_MIMETYPE:      str = f"{{{NS_OFFICE}}}mimetype"  # FACT-FODS-001: mimetype attribute identifies ODS flat-xml
ATTR_VERSION:       str = f"{{{NS_OFFICE}}}version"
ATTR_VALUE_TYPE:    str = f"{{{NS_OFFICE}}}value-type"
ATTR_VALUE:         str = f"{{{NS_OFFICE}}}value"
ATTR_BOOL_VALUE:    str = f"{{{NS_OFFICE}}}boolean-value"
ATTR_DATE_VALUE:    str = f"{{{NS_OFFICE}}}date-value"
ATTR_TIME_VALUE:    str = f"{{{NS_OFFICE}}}time-value"
ATTR_STRING_VALUE:  str = f"{{{NS_OFFICE}}}string-value"
ATTR_TABLE_NAME:    str = f"{{{NS_TABLE}}}name"
ATTR_COL_REPEAT:    str = f"{{{NS_TABLE}}}number-columns-repeated"
ATTR_ROW_REPEAT:    str = f"{{{NS_TABLE}}}number-rows-repeated"
ATTR_FORMULA:       str = f"{{{NS_TABLE}}}formula"
# R73 : merged-cell span metadata (ODF 1.3 section 9.1.4)
ATTR_COL_SPAN:      str = f"{{{NS_TABLE}}}number-columns-spanned"
ATTR_ROW_SPAN:      str = f"{{{NS_TABLE}}}number-rows-spanned"

# ---------------------------------------------------------------------------
# Warning codes (neutral model Warning entity -- Gate 5)
# ---------------------------------------------------------------------------

WARN_MISSING_MIMETYPE:       str = "MISSING_MIMETYPE"
WARN_UNEXPECTED_MIMETYPE:    str = "UNEXPECTED_MIMETYPE"
WARN_UNSUPPORTED_VALUE_TYPE: str = "UNSUPPORTED_VALUE_TYPE"
WARN_COVERED_CELL:           str = "COVERED_CELL"
WARN_UNSUPPORTED_ELEMENT:    str = "UNSUPPORTED_ELEMENT"
WARN_LARGE_REPEAT:           str = "LARGE_REPEAT"
WARN_UNKNOWN:                str = "UNKNOWN"
# R73 : deterministic formula presence warning (IR-FODS-008 transparency)
WARN_FORMULA_CELL:           str = "FORMULA_CELL"
