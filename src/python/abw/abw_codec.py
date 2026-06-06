"""
ABW codec — minimal AbiWord document API.

AbiWord (.abw) — plain XML AWML 1.0 format.
Uses xml.etree.ElementTree (stdlib) — no external dependencies.

Acquisition gates 1-7 passed. Implementation authorized: R20.
commercial_product_ready: false

Security note: DOCTYPE declarations are stripped before parsing.
The DTD at http://www.abisource.com/awml.dtd is unreachable (server down),
and ElementTree does not resolve external DTDs anyway (XXE-safe).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ABW_ROOT_TAG = "abiword"
ABW_MIME = "application/x-abiword"

# Maximum file size guard (64 MiB)
MAX_FILE_SIZE = 64 * 1024 * 1024


class AbwError(Exception):
    """Base exception for ABW codec errors."""


class AbwParseError(AbwError):
    """Raised when ABW parsing fails."""


def load(source: str | bytes | Path) -> dict[str, Any]:
    """Load and parse an ABW document.

    The returned model contains:
        is_abw (bool): True if valid AbiWord document.
        section_count (int): Number of <section> elements.
        paragraph_count (int): Number of <p> elements.
        paragraphs (list[str]): Text content of each paragraph.

    Args:
        source: Path to .abw file, bytes, or XML string.

    Returns:
        Parsed document model dict.

    Raises:
        AbwParseError: If source cannot be parsed.
        AbwError: For other load errors.
    """
    xml_bytes = _read_source(source)
    clean = _strip_doctype(xml_bytes)
    root = _parse_xml(clean)
    return _build_model(root)


def get_section_count(source: str | bytes | Path) -> int:
    """Return number of sections."""
    return load(source)["section_count"]


def get_paragraph_count(source: str | bytes | Path) -> int:
    """Return total paragraph count."""
    return load(source)["paragraph_count"]


def extract_text(source: str | bytes | Path) -> list[str]:
    """Extract all non-empty paragraph texts."""
    model = load(source)
    return [p for p in model.get("paragraphs", []) if p]


def create_abw(paragraphs: list[str]) -> dict[str, Any]:
    """Create a minimal ABW document model from a list of paragraph strings.

    Args:
        paragraphs: List of paragraph text strings (may be empty).

    Returns:
        Document model dict compatible with write_abw().
    """
    return {
        "is_abw": True,
        "section_count": 1,
        "paragraph_count": len(paragraphs),
        "paragraphs": list(paragraphs),
    }


def write_abw(model: dict[str, Any], dest: str | Path) -> None:
    """Serialize an ABW document model to an .abw file.

    Writes a well-formed AWML 1.0 XML file.  The DOCTYPE declaration is
    intentionally omitted (the DTD server at abisource.com is unreachable).

    Args:
        model: Document model dict as returned by load() or create_abw().
        dest:  Destination file path.

    Raises:
        AbwError: If model is invalid or dest cannot be written.
    """
    if not isinstance(model, dict) or not model.get("is_abw"):
        raise AbwError("model must be a valid ABW document dict (is_abw=True)")

    dest = Path(dest)
    paragraphs = model.get("paragraphs", [])

    root = ET.Element(
        ABW_ROOT_TAG,
        attrib={
            "template": "false",
            "styles": "unlocked",
            "version": "1.0",
            "fileformat": "1.0",
        },
    )
    section = ET.SubElement(root, "section")
    for text in paragraphs:
        p = ET.SubElement(section, "p")
        p.text = str(text)

    xml_str = ET.tostring(root, encoding="unicode", xml_declaration=False)
    content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str + "\n"

    try:
        dest.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise AbwError(f"Cannot write {dest}: {exc}") from exc


def export_to_txt(source: str | bytes | Path) -> str:
    """Export an ABW document to plain text.

    Extracts all paragraph texts and joins them with newlines.

    Args:
        source: Path to .abw file, bytes, or XML string.

    Returns:
        Plain text string with paragraphs joined by newlines.

    Raises:
        AbwParseError: If source cannot be parsed.
        AbwError: For other load errors.
    """
    model = load(source)
    paragraphs = model.get("paragraphs", [])
    return "\n".join(paragraphs)


def export_to_html(source: str | bytes | Path) -> str:
    """Export an ABW document to a minimal HTML string.

    Wraps each paragraph in an HTML ``<p>`` element.  Returns a complete
    ``<html><body>`` document suitable for display or downstream processing.
    Special characters (<, >, &, ") are escaped.

    Args:
        source: Path to .abw file, bytes, or XML string.

    Returns:
        HTML string with one ``<p>`` per paragraph.

    Raises:
        AbwParseError: If source cannot be parsed.
        AbwError: For other load errors.
    """
    _HTML_ESCAPE = str.maketrans({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"})
    model = load(source)
    paragraphs = model.get("paragraphs", [])
    lines = ["<!DOCTYPE html>", "<html>", "<body>"]
    for para in paragraphs:
        lines.append(f"<p>{para.translate(_HTML_ESCAPE)}</p>")
    lines += ["</body>", "</html>"]
    return "\n".join(lines)


def get_metadata(source: str | bytes | Path) -> dict[str, Any]:
    """Extract document metadata from an ABW file.

    Reads ``<meta>`` elements inside the ``<metadata>`` block (if present).
    Common keys include ``dc.title``, ``dc.creator``, ``dc.description``,
    and ``abiword.date_last_changed``.

    Returns an empty dict when no metadata block is present (e.g. documents
    created by :func:`create_abw`).

    Args:
        source: Path to .abw file, bytes, or XML string.

    Returns:
        Dict mapping meta key strings to value strings.

    Raises:
        AbwParseError: If source cannot be parsed.
        AbwError: For other load errors.
    """
    xml_bytes = _read_source(source)
    clean = _strip_doctype(xml_bytes)
    root = _parse_xml(clean)
    meta: dict[str, str] = {}
    for meta_block in root.iter("metadata"):
        for m in meta_block:
            key = m.get("key") or m.tag
            value = m.get("value") or (m.text or "")
            if key:
                meta[key] = value
    return meta


def probe_abw(source) -> bool:
    """Probe whether source is a valid ABW (AbiWord) document.

    Checks for the abiword root element without full parsing.
    Does not raise on malformed input - returns False instead.

    Args:
        source: Path to a file, bytes, or XML string to probe.

    Returns:
        True if source appears to be an ABW document, False otherwise.
    """
    try:
        raw = _read_source(source)
        snippet = raw[:4096].decode("utf-8", errors="replace")
        snippet_stripped = _strip_doctype(snippet.encode())
        # ABW files start with optional XML declaration, then <abiword ...>
        return "<abiword" in snippet_stripped
    except Exception:
        return False

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_source(source: str | bytes | Path) -> bytes:
    if isinstance(source, Path):
        _check_size(source)
        return source.read_bytes()
    elif isinstance(source, str) and not source.strip().startswith("<") and not source.strip().startswith("<?"):
        path = Path(source)
        _check_size(path)
        return path.read_bytes()
    elif isinstance(source, str):
        return source.encode("utf-8")
    elif isinstance(source, (bytes, bytearray)):
        if len(source) > MAX_FILE_SIZE:
            raise AbwError(f"Input exceeds {MAX_FILE_SIZE} byte limit")
        return bytes(source)
    else:
        raise AbwError(f"Unsupported source type: {type(source).__name__}")


def _check_size(path: Path) -> None:
    if not path.exists():
        raise AbwParseError(f"File not found: {path}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise AbwError(f"File size {size} exceeds {MAX_FILE_SIZE} byte limit")


def _strip_doctype(xml_bytes: bytes) -> str:
    """Strip DOCTYPE declaration to avoid DTD resolution attempts."""
    xml_str = xml_bytes.decode("utf-8", errors="replace")
    lines = xml_str.splitlines()
    filtered = [line for line in lines if not line.strip().startswith("<!DOCTYPE")]
    return "\n".join(filtered)


def _parse_xml(xml_str: str) -> ET.Element:
    """Parse XML string safely (XXE-safe via ElementTree)."""
    try:
        return ET.fromstring(xml_str)
    except ET.ParseError as exc:
        raise AbwParseError(f"XML parse error: {exc}") from exc


def _build_model(root: ET.Element) -> dict[str, Any]:
    """Build a document model from the parsed XML root."""
    if root.tag != ABW_ROOT_TAG:
        raise AbwParseError(
            f"Root element must be 'abiword', got {root.tag!r}"
        )

    sections = list(root.iter("section"))
    paragraphs = []
    for p in root.iter("p"):
        text = "".join(p.itertext()).strip()
        paragraphs.append(text)

    return {
        "is_abw": True,
        "section_count": len(sections),
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
    }
