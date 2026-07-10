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

    # Additional drawing analysis properties (FACT-FODG-001)

    @property
    def is_multi_page(self) -> bool:
        """True if the drawing has more than one page."""
        return self.page_count > 1

    @property
    def has_multiple_shapes(self) -> bool:
        """True if the drawing contains more than one shape."""
        return self.shapes_total > 1

    @property
    def shapes_per_page(self) -> float:
        """Average number of shapes per page. Returns 0.0 if no pages."""
        if self.page_count == 0:
            return 0.0
        return self.shapes_total / self.page_count

    # Density and complexity properties (FACT-FODG-001 R1246)

    @property
    def is_dense(self) -> bool:
        """True if shapes_per_page > 10."""
        return self.shapes_per_page > 10

    @property
    def is_complex(self) -> bool:
        """True if has_shapes and is_multi_page."""
        return self.has_shapes and self.is_multi_page

    @property
    def max_shapes_on_page(self) -> int:
        """Maximum shape_count on any page; 0 if no pages."""
        pages = self.pages
        if not pages:
            return 0
        return max(p.get("shape_count", 0) for p in pages)

    # Shape distribution properties (FACT-FODG-001 R1266)

    @property
    def min_shapes_on_page(self) -> int:
        """Minimum shape_count on any page; 0 if no pages."""
        pages = self.pages
        if not pages:
            return 0
        return min(p.get("shape_count", 0) for p in pages)

    @property
    def shape_range(self) -> int:
        """max_shapes_on_page - min_shapes_on_page; 0 if no pages."""
        pages = self.pages
        if not pages:
            return 0
        counts = [p.get("shape_count", 0) for p in pages]
        return max(counts) - min(counts)

    @property
    def is_uniform_density(self) -> bool:
        """True if all pages have the same shape count."""
        pages = self.pages
        if not pages:
            return True
        counts = [p.get("shape_count", 0) for p in pages]
        return len(set(counts)) == 1

    def add_page(self, name: str | None = None, texts: list[str] | None = None) -> None:
        """Append a new page to this document in place.

        Args:
            name:  Page name (default: auto-generated 'Page<N>').
            texts: List of text strings; each becomes a shape on the page.

        Raises:
            FodgError: If name is not str or None.
        """
        from .fodg_codec import FodgError, create_fodg
        if name is not None and not isinstance(name, str):
            raise FodgError("name must be a str or None")
        pages = self._data.setdefault("pages", [])
        idx = len(pages)
        auto_name = name if name is not None else f"Page{idx + 1}"
        new_page = create_fodg([{"name": auto_name, "texts": texts or []}])["pages"][0]
        pages.append(new_page)
        self._data["page_count"] = len(pages)
        self._data["shapes_total"] = sum(p.get("shape_count", 0) for p in pages)

    def save_to_file(self, path: "str | Path") -> None:
        """Save this document to a .fodg file (flat OpenDocument XML).

        Raises:
            FodgError: If path is empty or write fails.
        """
        from .fodg_codec import FodgError, write_fodg
        if not path:
            raise FodgError("path must not be empty")
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        write_fodg(self._data, dest)

    def to_dict(self) -> dict[str, Any]:
        """Return document summary as a dict."""
        return {
            "is_fodg": self.is_fodg,
            "page_count": self.page_count,
            "shapes_total": self.shapes_total,
        }

    def __repr__(self) -> str:
        return f"FodgDocument(page_count={self.page_count}, shapes_total={self.shapes_total})"
