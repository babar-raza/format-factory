"""
odt_parser.py — ODT streaming parser for format-factory-odt.

Public API:
  parse_odt(file_path)        — returns result dict (never raises)
  parse_odt_strict(file_path) — raises OdtError on failure
  probe_odt(file_path)        — returns container metadata dict

Implements Gate 4 prototype scope per R26 parser plan.
Technology: Python zipfile + xml.etree.ElementTree (stdlib, XXE-safe).

License: Apache-2.0
"""

from __future__ import annotations

import os
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ODT constants
ODT_MIMETYPE = "application/vnd.oasis.opendocument.text"
MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB
MAX_ZIP_ENTRIES = 1000

# ODF namespaces
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
}


UNSUPPORTED_FEATURES = frozenset({
    "tables",
    "images",
    "embedded_objects",
    "footnotes",
    "endnotes",
    "annotations",
    "tracked_changes",
    "fields",
    "bookmarks",
    "cross_references",
    "table_of_contents",
    "indexes",
    "text_frames",
    "sections",
    "master_pages",
    "page_styles",
    "character_styles",
    "macros",
    "protection",
    "encryption",
    "forms",
})

SUPPORTED_FEATURES = frozenset({
    "paragraph_extraction",
    "heading_extraction",
    "heading_level_detection",
    "list_item_extraction",
    "text_style_name",
    "element_order_preservation",
    "container_validation",
    "mimetype_verification",
    "size_guard",
    "probe_without_parse",
})


def get_capabilities() -> dict[str, Any]:
    """Return supported/unsupported feature declarations for ODT parser."""
    return {
        "format": "odt",
        "gate": 5,
        "supported": sorted(SUPPORTED_FEATURES),
        "unsupported": sorted(UNSUPPORTED_FEATURES),
        "commercial_product_ready": False,
        "max_file_size": MAX_FILE_SIZE,
        "max_zip_entries": MAX_ZIP_ENTRIES,
    }


class OdtError(Exception):
    """Base exception for ODT parser errors."""


class OdtInvalidContainerError(OdtError):
    """Raised when the ZIP container is invalid or missing required entries."""


class OdtSizeError(OdtError):
    """Raised when the file or decompressed content exceeds size limits."""


@dataclass
class OdtParagraph:
    text: str = ""
    style: str = ""


@dataclass
class OdtHeading:
    text: str = ""
    level: int = 1


@dataclass
class OdtListItem:
    text: str = ""


@dataclass
class OdtDocument:
    paragraphs: list[OdtParagraph] = field(default_factory=list)
    headings: list[OdtHeading] = field(default_factory=list)
    elements: list[OdtParagraph | OdtHeading | OdtListItem] = field(default_factory=list)
    path: str = ""


def _check_file_size(path: Path) -> None:
    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        raise OdtSizeError(
            f"File size {size} bytes exceeds limit of {MAX_FILE_SIZE} bytes"
        )


def _validate_container(zf: zipfile.ZipFile) -> None:
    names = zf.namelist()
    if len(names) > MAX_ZIP_ENTRIES:
        raise OdtSizeError(
            f"ZIP has {len(names)} entries, exceeds limit of {MAX_ZIP_ENTRIES}"
        )
    if "mimetype" not in names:
        raise OdtInvalidContainerError("Missing 'mimetype' entry in ODT container")
    mimetype = zf.read("mimetype").decode("utf-8", errors="replace").strip()
    if mimetype != ODT_MIMETYPE:
        raise OdtInvalidContainerError(
            f"Invalid mimetype: expected '{ODT_MIMETYPE}', got '{mimetype}'"
        )
    if "content.xml" not in names:
        raise OdtInvalidContainerError("Missing 'content.xml' in ODT container")
    total = sum(info.file_size for info in zf.infolist())
    if total > MAX_FILE_SIZE:
        raise OdtSizeError(
            f"Total decompressed size {total} exceeds limit of {MAX_FILE_SIZE}"
        )


def _parse_content_xml(content_bytes: bytes) -> OdtDocument:
    root = ET.fromstring(content_bytes)
    doc = OdtDocument()

    body = root.find(f"{{{NS['office']}}}body")
    if body is None:
        return doc
    text_body = body.find(f"{{{NS['office']}}}text")
    if text_body is None:
        return doc

    for elem in text_body:
        tag = elem.tag

        if tag == f"{{{NS['text']}}}p":
            text = "".join(elem.itertext())
            style = elem.get(f"{{{NS['text']}}}style-name", "")
            para = OdtParagraph(text=text, style=style)
            doc.paragraphs.append(para)
            doc.elements.append(para)

        elif tag == f"{{{NS['text']}}}h":
            text = "".join(elem.itertext())
            level_str = elem.get(f"{{{NS['text']}}}outline-level", "1")
            try:
                level = int(level_str)
            except ValueError:
                level = 1
            heading = OdtHeading(text=text, level=level)
            doc.headings.append(heading)
            doc.elements.append(heading)

        elif tag == f"{{{NS['text']}}}list":
            for item in elem.findall(f"{{{NS['text']}}}list-item"):
                for p in item.findall(f"{{{NS['text']}}}p"):
                    text = "".join(p.itertext())
                    li = OdtListItem(text=text)
                    doc.elements.append(li)

    return doc


def parse_odt_strict(file_path: str | Path) -> OdtDocument:
    """Parse an ODT file, raising OdtError on any problem."""
    path = Path(file_path)
    _check_file_size(path)
    try:
        with zipfile.ZipFile(path, "r") as zf:
            _validate_container(zf)
            content = zf.read("content.xml")
    except zipfile.BadZipFile as exc:
        raise OdtInvalidContainerError(f"Invalid ZIP: {exc}") from exc
    except OdtError:
        raise
    except OSError as exc:
        raise OdtError(f"Cannot read file: {exc}") from exc

    doc = _parse_content_xml(content)
    doc.path = str(path)
    return doc


def parse_odt(file_path: str | Path) -> dict[str, Any]:
    """Parse an ODT file, returning a result dict (never raises)."""
    try:
        doc = parse_odt_strict(file_path)
        return {
            "ok": True,
            "path": doc.path,
            "paragraph_count": len(doc.paragraphs),
            "heading_count": len(doc.headings),
            "element_count": len(doc.elements),
            "paragraphs": [{"text": p.text, "style": p.style} for p in doc.paragraphs],
            "headings": [{"text": h.text, "level": h.level} for h in doc.headings],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "error_type": type(exc).__name__}


def probe_odt(file_path: str | Path) -> dict[str, Any]:
    """Probe an ODT file for container metadata without full parse."""
    path = Path(file_path)
    result: dict[str, Any] = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        _check_file_size(path)
        with zipfile.ZipFile(path, "r") as zf:
            _validate_container(zf)
            result["valid_container"] = True
            result["entries"] = zf.namelist()
            result["mimetype"] = zf.read("mimetype").decode("utf-8", errors="replace").strip()
    except Exception as exc:
        result["valid_container"] = False
        result["error"] = str(exc)
    return result


def odt_word_count(file_path: str | Path) -> int:
    """Count total words across all paragraphs, headings, and list items in an ODT file."""
    doc = parse_odt_strict(file_path)
    total = 0
    for elem in doc.elements:
        text = getattr(elem, "text", "")
        if isinstance(text, str):
            total += len(text.split())
    return total


def odt_heading_count(file_path: str | Path) -> int:
    """Count the number of headings in an ODT document."""
    doc = parse_odt_strict(file_path)
    return len(doc.headings)


def odt_paragraph_count(file_path: str | Path) -> int:
    """Count the number of paragraphs in an ODT document."""
    doc = parse_odt_strict(file_path)
    return len(doc.paragraphs)


def odt_char_count(file_path: str | Path) -> int:
    """Return the total character count across all paragraphs in an ODT document."""
    doc = parse_odt_strict(file_path)
    return sum(len(p.text) for p in doc.paragraphs)


def odt_list_count(file_path: str | Path) -> int:
    """Count the number of top-level lists in an ODT document.

    Counts text:list elements that are direct children of the text body.
    ODF 1.3 §5.3.1 — text:list is the element for ordered/unordered lists.

    Args:
        file_path: Path to .odt file.

    Returns:
        Number of top-level text:list elements.
    """
    path = Path(file_path)
    _check_file_size(path)
    with zipfile.ZipFile(path, "r") as zf:
        _validate_container(zf)
        content = zf.read("content.xml")
    root = ET.fromstring(content)
    body = root.find(f"{{{NS['office']}}}body")
    if body is None:
        return 0
    text_body = body.find(f"{{{NS['office']}}}text")
    if text_body is None:
        return 0
    list_tag = f"{{{NS['text']}}}list"
    return sum(1 for child in text_body if child.tag == list_tag)


def odt_table_count(file_path: str | Path) -> int:
    """Count the number of tables in an ODT document.

    Counts table:table elements that are direct children of the text body.
    ODF 1.3 §9.1.2 — table:table is the element for tables in text documents.

    Args:
        file_path: Path to .odt file.

    Returns:
        Number of table:table elements in the text body.
    """
    path = Path(file_path)
    _check_file_size(path)
    with zipfile.ZipFile(path, "r") as zf:
        _validate_container(zf)
        content = zf.read("content.xml")
    root = ET.fromstring(content)
    body = root.find(f"{{{NS['office']}}}body")
    if body is None:
        return 0
    text_body = body.find(f"{{{NS['office']}}}text")
    if text_body is None:
        return 0
    table_tag = f"{{{NS['table']}}}table"
    return sum(1 for child in text_body if child.tag == table_tag)


def odt_sentence_count(file_path: str | Path) -> int:
    """Estimate the number of sentences in an ODT document.

    Counts sentence-ending punctuation (.!?) across all paragraphs and
    headings.  This is a heuristic — abbreviations like "Dr." will be
    over-counted, but for most prose it gives a reasonable approximation.

    Args:
        file_path: Path to .odt file.

    Returns:
        Estimated number of sentences.
    """
    import re
    doc = parse_odt_strict(file_path)
    total = 0
    for elem in doc.elements:
        text = getattr(elem, "text", "")
        if isinstance(text, str) and text:
            total += len(re.findall(r"[.!?]+", text))
    return total


def odt_average_word_length(file_path: str | Path) -> float:
    """Return the average word length (characters per word) in an ODT document.

    Args:
        file_path: Path to .odt file.

    Returns:
        Float average word length. Returns 0.0 if document has no words.
    """
    doc = parse_odt_strict(file_path)
    words: list[str] = []
    for elem in doc.elements:
        text = getattr(elem, "text", "")
        if isinstance(text, str) and text:
            words.extend(text.split())
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def odt_unique_word_count(file_path: str | Path) -> int:
    """Return the number of distinct words (case-insensitive) in an ODT document.

    Args:
        file_path: Path to .odt file.

    Returns:
        Integer count of unique words.
    """
    doc = parse_odt_strict(file_path)
    unique: set[str] = set()
    for elem in doc.elements:
        text = getattr(elem, "text", "")
        if isinstance(text, str) and text:
            unique.update(w.lower() for w in text.split())
    return len(unique)


def odt_longest_paragraph(file_path: str | Path) -> int:
    """Return the character count of the longest paragraph in an ODT document.

    Returns 0 if no paragraphs exist.
    """
    doc = parse_odt_strict(file_path)
    max_len = 0
    for elem in doc.elements:
        elem_type = getattr(elem, "type", getattr(elem, "tag", ""))
        text = getattr(elem, "text", "")
        if isinstance(text, str) and ("paragraph" in str(elem_type).lower() or "p" == str(elem_type).lower()):
            max_len = max(max_len, len(text))
    if max_len == 0:
        for elem in doc.elements:
            text = getattr(elem, "text", "")
            if isinstance(text, str):
                max_len = max(max_len, len(text))
    return max_len


def odt_has_tables(file_path: str | Path) -> bool:
    """Return True if the ODT document contains at least one table."""
    return odt_table_count(file_path) > 0
