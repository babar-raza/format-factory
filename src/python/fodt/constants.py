"""
constants.py -- FODT parser constants for format-factory-fodt.

ODF namespace URIs, qualified element/attribute names, limits, and
format identity constants used across the FODT Python FOSS package.

ODF 1.3 spec citation:
  source: ODF 1.3 Part 3 (schema spec)
  source_hash: sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066

License: Apache-2.0
Package: format-factory-fodt v0.1.0
"""

# ---------------------------------------------------------------------------
# Format identity
# ---------------------------------------------------------------------------

FORMAT_ID: str = "fodt"
SPEC_VERSION: str = "ODF 1.3"
PACKAGE_VERSION: str = "0.1.0"

# ---------------------------------------------------------------------------
# MIME type (IR-FODT-001 -- FFODT-002)
# ---------------------------------------------------------------------------

EXPECTED_MIMETYPE: str = (
    "application/vnd.oasis.opendocument.text-flat-xml"
)

# ---------------------------------------------------------------------------
# File size guard (IR-FODT-002 -- FFODT-009)
# ---------------------------------------------------------------------------

MAX_FILE_BYTES: int = 100 * 1024 * 1024  # 100 MB

# ---------------------------------------------------------------------------
# ODF 1.3 XML namespace URIs (ODF 1.3 section 3.1.2)
# ---------------------------------------------------------------------------

NS_OFFICE: str = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
NS_TABLE: str  = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
NS_TEXT: str   = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
NS_DRAW: str   = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
NS_XLINK: str  = "http://www.w3.org/1999/xlink"

# ---------------------------------------------------------------------------
# Qualified element names (Clark notation: {uri}localname)
# ---------------------------------------------------------------------------

QN_DOCUMENT:    str = f"{{{NS_OFFICE}}}document"
QN_BODY:        str = f"{{{NS_OFFICE}}}body"
QN_TEXT:        str = f"{{{NS_OFFICE}}}text"
QN_SCRIPTS:     str = f"{{{NS_OFFICE}}}scripts"

QN_TEXT_P:      str = f"{{{NS_TEXT}}}p"
QN_TEXT_H:      str = f"{{{NS_TEXT}}}h"
QN_TEXT_SPAN:   str = f"{{{NS_TEXT}}}span"
QN_TEXT_A:      str = f"{{{NS_TEXT}}}a"
QN_LIST:        str = f"{{{NS_TEXT}}}list"
QN_LIST_ITEM:   str = f"{{{NS_TEXT}}}list-item"

QN_TABLE:       str = f"{{{NS_TABLE}}}table"
QN_TABLE_ROW:   str = f"{{{NS_TABLE}}}table-row"
QN_TABLE_CELL:  str = f"{{{NS_TABLE}}}table-cell"

QN_DRAW_FRAME:  str = f"{{{NS_DRAW}}}frame"
QN_DRAW_IMAGE:  str = f"{{{NS_DRAW}}}image"

# ---------------------------------------------------------------------------
# Qualified attribute names
# ---------------------------------------------------------------------------

ATTR_MIMETYPE:       str = f"{{{NS_OFFICE}}}mimetype"
ATTR_VERSION:        str = f"{{{NS_OFFICE}}}version"
ATTR_OUTLINE_LEVEL:  str = f"{{{NS_TEXT}}}outline-level"
ATTR_TABLE_NAME:     str = f"{{{NS_TABLE}}}name"
ATTR_STYLE_NAME:     str = f"{{{NS_TEXT}}}style-name"
ATTR_XLINK_HREF:     str = f"{{{NS_XLINK}}}href"
ATTR_XLINK_TYPE:     str = f"{{{NS_XLINK}}}type"

# ---------------------------------------------------------------------------
# Text field namespace prefix -- detect text:* field elements (IR-FODT-009)
# The prefix for text-field QN detection uses the NS_TEXT namespace.
# ---------------------------------------------------------------------------

TEXT_FIELD_LOCAL_NAMES: frozenset = frozenset({
    "date", "time", "page-number", "page-count", "chapter",
    "variable-get", "variable-set", "sequence", "database-display",
    "user-field-get", "bookmark-ref",
})

# ---------------------------------------------------------------------------
# Warning codes
# ---------------------------------------------------------------------------

WARN_MISSING_MIMETYPE:       str = "MISSING_MIMETYPE"
WARN_UNEXPECTED_MIMETYPE:    str = "UNEXPECTED_MIMETYPE"
WARN_UNSUPPORTED_ELEMENT:    str = "UNSUPPORTED_ELEMENT"
WARN_UNKNOWN:                str = "UNKNOWN"
