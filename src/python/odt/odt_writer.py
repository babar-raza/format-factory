"""ODT writer — create OpenDocument Text (.odt) files from plain text or OdtDocument.

Spec authority : OpenDocument Format 1.3 (OASIS ODF TC)
QName         : office:document
Namespace URI : urn:oasis:names:tc:opendocument:xmlns:office:1.0
Spec fact ref : FACT-ODT-001

Gap closure: GAP-PROD-INV-WRITE-001 (ODT was read-only; this adds write capability)

Functions:
    write_odt(paragraphs, dest)  — write list of paragraph strings to .odt file
    odt_from_text(text, dest)    — write a plain text string as an ODT document
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

# XML namespaces used in ODT content.xml
_NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
_NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
_ODT_MIMETYPE = "application/vnd.oasis.opendocument.text"


def _build_content_xml(paragraphs: list[str]) -> str:
    """Build a minimal content.xml string for the given paragraphs."""

    # Build paragraph elements
    para_xml = ""
    for p in paragraphs:
        # Escape XML special characters
        escaped = (
            p.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        para_xml += f'      <text:p>{escaped}</text:p>\n'

    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<office:document-content'
        ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
        ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
        ' office:version="1.3">\n'
        '  <office:body>\n'
        '    <office:text>\n'
        f'{para_xml}'
        '    </office:text>\n'
        '  </office:body>\n'
        '</office:document-content>\n'
    )
    return content


def write_odt(
    paragraphs: list[str],
    dest: str | Path,
    *,
    heading: str | None = None,
) -> Path:
    """Write a list of paragraph strings to an ODT file.

    Creates a minimal but valid ODT container (ZIP with mimetype + content.xml).

    Args:
        paragraphs: List of paragraph text strings to write.
        dest: Destination path for the .odt file.
        heading: Optional document heading inserted before paragraphs.

    Returns:
        Path to the written file.

    Raises:
        OSError: If the destination path cannot be written.
    """
    out = Path(dest)
    all_paras = []
    if heading:
        all_paras.append(heading)
    all_paras.extend(paragraphs)

    content_xml = _build_content_xml(all_paras)

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # mimetype must be stored (not compressed) and be the first entry
        zf.writestr(
            zipfile.ZipInfo("mimetype"),
            _ODT_MIMETYPE,
        )
        zf.writestr("content.xml", content_xml)

    return out


def odt_from_text(text: str, dest: str | Path) -> Path:
    """Write a plain text string as an ODT document.

    Splits text on newlines; each non-empty line becomes a paragraph.

    Args:
        text: Plain text content to write.
        dest: Destination path for the .odt file.

    Returns:
        Path to the written file.
    """
    paragraphs = [line for line in text.splitlines() if line.strip()]
    return write_odt(paragraphs, dest)


def odt_from_model(model: Any, dest: str | Path) -> Path:
    """Write an OdtDocument (or neutral model dict) to an ODT file.

    Accepts:
        - OdtDocument dataclass (from parse_odt_strict)
        - dict with 'paragraphs' key (from parse_odt neutral model)
        - list of paragraph strings

    Args:
        model: Source document model.
        dest: Destination path for the .odt file.

    Returns:
        Path to the written file.
    """
    if isinstance(model, list):
        paragraphs = [str(p) for p in model]
    elif isinstance(model, dict):
        raw = model.get("paragraphs", [])
        paragraphs = [p if isinstance(p, str) else str(p) for p in raw]
    else:
        # OdtDocument dataclass — access .paragraphs
        raw = getattr(model, "paragraphs", [])
        paragraphs = [
            p.text if hasattr(p, "text") else str(p) for p in raw
        ]
    return write_odt(paragraphs, dest)
