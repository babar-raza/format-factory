"""Domain model classes for FODG (Flat OpenDocument Drawing).

Classes:
    FodgDocument — typed wrapper over the dict-based neutral model from load()

spec_qname: office:document
spec_fact_ref: see shared/qname-registry/fodg.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class FodgDocument:
    """Typed domain model for a Flat OpenDocument Drawing (.fodg) file.

    Wraps the neutral model dict returned by fodg_codec.load().
    Neutral model keys: is_fodg (bool), page_count (int),
    pages (list[dict]), shapes_total (int).
    """

    spec_qname: ClassVar[str] = "office:document"
    spec_fact_ref: ClassVar[str] = "FACT-FODG-001"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name: ClassVar[str] = "document"
    facade_names: ClassVar[list] = []

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str | Path) -> "FodgDocument":
        """Load a FODG file and return a FodgDocument."""
        from .fodg_codec import load
        return cls(load(path))

    @property
    def page_count(self) -> int:
        """Number of drawing pages."""
        return int(self._data.get("page_count", 0))

    @property
    def shapes_total(self) -> int:
        """Total number of shapes across all pages."""
        return int(self._data.get("shapes_total", 0))

    @property
    def pages(self) -> list[dict[str, Any]]:
        """List of page dicts (name, style, shape_count, text_content)."""
        return list(self._data.get("pages", []))

    @property
    def is_fodg(self) -> bool:
        """True if the file was recognised as a valid FODG document."""
        return bool(self._data.get("is_fodg", False))

    # Drawing dimension properties (FACT-FODG-001)
    @property
    def is_empty(self) -> bool:
        """True if the drawing has no pages."""
        return self.page_count == 0

    @property
    def is_single_page(self) -> bool:
        """True if the drawing has exactly one page."""
        return self.page_count == 1

    @property
    def has_shapes(self) -> bool:
        """True if the drawing contains at least one shape."""
        return self.shapes_total > 0

    def to_dict(self) -> dict[str, Any]:
        """Return document summary as a dict."""
        return {
            "is_fodg": self.is_fodg,
            "page_count": self.page_count,
            "shapes_total": self.shapes_total,
        }

    def __repr__(self) -> str:
        return f"FodgDocument(page_count={self.page_count}, shapes_total={self.shapes_total})"
