"""Domain classes for FODT — thin wrappers over the dict-based neutral model.

Classes:
    FodtDocument — wraps the document dict from parse_fodt()
    FodtParagraph — wraps a block dict (paragraph or heading)
    FodtSpan — wraps an inline span/formatting element

These preserve the existing function API while providing a class-based interface.
"""

from __future__ import annotations

from typing import Any

from .Compat.fodt_paragraph import FodtParagraph as _CompatParagraph


class FodtSpan:
    """Wraps an inline text span from a paragraph."""

    spec_qname = "text:span"
    spec_fact_ref = "FACT-FODT-006"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def text(self) -> str:
        return self._data.get("text", "")

    @property
    def style_name(self) -> str:
        return self._data.get("style_name", "")

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"FodtSpan(text={self.text!r})"


class FodtParagraph:
    """Wraps a block dict (paragraph or heading) from the FODT neutral model."""

    spec_qname = "text:p"
    spec_fact_ref = "FACT-FODT-003"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def kind(self) -> str:
        return self._data.get("kind", "paragraph")

    @property
    def text(self) -> str:
        return self._data.get("text", "")

    @property
    def style_name(self) -> str:
        return self._data.get("style_name", "")

    @property
    def outline_level(self) -> int | None:
        return self._data.get("outline_level")

    @property
    def spans(self) -> list[FodtSpan]:
        return [FodtSpan(s) for s in self._data.get("spans", [])]

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"FodtParagraph(kind={self.kind!r}, text={self.text!r})"


class FodtDocument:
    """Wraps a document dict from parse_fodt() with a class-based interface."""

    spec_qname = "office:document"
    spec_fact_ref = "FACT-FODT-001"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> FodtDocument:
        """Parse a FODT file and wrap the result."""
        from .parser import parse_fodt
        return cls(parse_fodt(path))

    @property
    def format_id(self) -> str:
        return self._data.get("format_id", "fodt")

    @property
    def odf_version(self) -> str:
        return self._data.get("odf_version", "")

    @property
    def warnings(self) -> list[dict[str, Any]]:
        return self._data.get("warnings", [])

    def paragraphs(self) -> list[_CompatParagraph]:
        """Return all blocks as Compat.FodtParagraph instances (spec-backed facade)."""
        return [_CompatParagraph(b) for b in self._data.get("blocks", [])]

    def headings(self) -> list[_CompatParagraph]:
        """Return only heading blocks as Compat.FodtParagraph instances."""
        return [
            _CompatParagraph(b) for b in self._data.get("blocks", [])
            if b.get("kind") == "heading"
        ]

    @property
    def block_count(self) -> int:
        return len(self._data.get("blocks", []))

    @property
    def table_count(self) -> int:
        return len(self._data.get("tables", []))

    @property
    def list_count(self) -> int:
        return len(self._data.get("lists", []))

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying document dict."""
        return self._data

    def __repr__(self) -> str:
        return f"FodtDocument(blocks={self.block_count}, tables={self.table_count})"


# ---------------------------------------------------------------------------
# Module-level convenience functions (gap-ledger closure)
# ---------------------------------------------------------------------------

def from_file(file_path: "str | Any") -> dict[str, Any]:
    """Parse a FODT file and return the neutral model document dict."""
    from pathlib import Path as _P
    from .parser import parse_fodt_strict
    return parse_fodt_strict(_P(file_path))


def odf_version(document: dict[str, Any]) -> str:
    """Return the ODF version string from a parsed document."""
    return document.get("odf_version", "")


def paragraphs(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all paragraph/heading blocks from a parsed document."""
    return list(document.get("blocks", []))


def to_dict(document: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-safe copy of the document dict."""
    import copy
    result = copy.deepcopy(document)
    return {k: v for k, v in result.items() if not k.startswith("_")}


def kind(block: dict[str, Any]) -> str:
    """Return the kind of a block ('paragraph', 'heading', etc.)."""
    return block.get("kind", "paragraph")


def style_name(block: dict[str, Any]) -> str:
    """Return the style name of a block."""
    return block.get("style_name", "")


def outline_level(block: dict[str, Any]) -> "int | None":
    """Return the outline level of a heading block, or None."""
    return block.get("outline_level")


def collect_list_items(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all list items from a parsed document."""
    items: list[dict[str, Any]] = []
    for lst in document.get("lists", []):
        for item in lst.get("items", []):
            items.append(item)
    return items
