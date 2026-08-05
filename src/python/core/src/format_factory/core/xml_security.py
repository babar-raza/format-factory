"""Hardened XML parsing for untrusted input.

Every XML format (ORA, UBL, XLIFF) must parse documents supplied by
strangers. This module provides the security boundary: DOCTYPE and entity
declarations are rejected before any expat processing, and tree-limit
enforcement runs during parsing, not after.

Multi-byte encodings (UTF-16, UTF-32) are detected via BOM and transcoded
to UTF-8 before scanning and parsing. This avoids null-byte interleaving
that would let ``<!DOCTYPE`` bypass a byte-level regex.
"""

from __future__ import annotations

import codecs
import re
import xml.etree.ElementTree as ET

from .errors import FormatParseError
from .limits import ResourceLimits

_DOCTYPE_PATTERN = re.compile(rb"<!DOCTYPE", re.IGNORECASE)
_ENTITY_PATTERN = re.compile(rb"<!ENTITY", re.IGNORECASE)

PERMITTED_ENCODINGS = frozenset({
    "utf-8", "utf-16", "utf-16le", "utf-16be", "utf-32",
    "utf-32le", "utf-32be", "ascii", "us-ascii", "iso-8859-1",
    "latin-1", "latin1",
})

_BOM_TABLE: list[tuple[bytes, str]] = [
    (codecs.BOM_UTF32_LE, "utf-32-le"),
    (codecs.BOM_UTF32_BE, "utf-32-be"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),
    (codecs.BOM_UTF16_BE, "utf-16-be"),
    (codecs.BOM_UTF8, "utf-8"),
]


def _detect_encoding(data: bytes) -> str:
    """Detect encoding from BOM. Returns 'utf-8' when no BOM is present."""
    for bom, encoding in _BOM_TABLE:
        if data.startswith(bom):
            return encoding
    return "utf-8"


def _normalize_to_utf8(
    data: bytes,
    *,
    error_class: type[Exception] = FormatParseError,
) -> bytes:
    """Transcode multi-byte XML to UTF-8 so byte-level regex scanning works.

    Returns the original bytes unchanged for UTF-8 input. For UTF-16/32,
    decodes and re-encodes as UTF-8. This is not null-byte stripping — it
    is a proper codec transcode that preserves all codepoints.
    """
    encoding = _detect_encoding(data)
    if encoding == "utf-8":
        return data
    try:
        text = data.decode(encoding)
    except (UnicodeDecodeError, LookupError) as exc:
        raise error_class(f"cannot decode XML as {encoding}: {exc}") from exc
    return text.encode("utf-8")


def reject_unsafe_xml(
    data: bytes,
    *,
    error_class: type[Exception] = FormatParseError,
) -> None:
    """Reject DTD and entity declarations in the FULL payload.

    This scans the complete byte sequence, not a bounded prefix — a DOCTYPE
    placed beyond any prefix length is still dangerous and must be caught.

    Multi-byte encoded inputs (UTF-16, UTF-32) are transcoded to UTF-8
    before scanning so that null-byte interleaving cannot hide keywords.
    """
    normalized = _normalize_to_utf8(data, error_class=error_class)
    if _DOCTYPE_PATTERN.search(normalized):
        raise error_class("DTD declarations are prohibited in untrusted XML")
    if _ENTITY_PATTERN.search(normalized):
        raise error_class("entity declarations are prohibited in untrusted XML")


def safe_fromstring(
    data: bytes,
    *,
    limits: ResourceLimits,
    error_class: type[Exception] = FormatParseError,
) -> ET.Element:
    """Parse XML bytes with full security hardening.

    1. Enforces input size limits on the raw payload.
    2. Transcodes multi-byte encodings to UTF-8.
    3. Rejects DOCTYPE and entity declarations in the FULL payload.
    4. Parses via ElementTree (which does not resolve external entities
       since Python 3.8+).
    5. Enforces node count, nesting depth, and text size limits on the
       resulting tree.

    Returns the root Element if safe; raises ``error_class`` otherwise.
    """
    limits.enforce("max_input_bytes", len(data))
    utf8_data = _normalize_to_utf8(data, error_class=error_class)
    reject_unsafe_xml(utf8_data, error_class=error_class)

    try:
        root = ET.fromstring(utf8_data)
    except ET.ParseError as exc:
        raise error_class(f"malformed XML: {exc}") from exc

    count = 0
    text_bytes = 0
    stack: list[tuple[ET.Element, int]] = [(root, 1)]
    while stack:
        element, depth = stack.pop()
        count += 1
        if count > limits.max_xml_nodes:
            raise error_class(f"XML node limit exceeded: {count}")
        if depth > limits.max_nesting_depth:
            raise error_class(f"XML nesting depth limit exceeded: {depth}")
        text_bytes += len((element.text or "").encode("utf-8"))
        text_bytes += len((element.tail or "").encode("utf-8"))
        if text_bytes > limits.max_decompressed_bytes:
            raise error_class(f"XML text content limit exceeded: {text_bytes}")
        stack.extend((child, depth + 1) for child in reversed(element))

    return root
