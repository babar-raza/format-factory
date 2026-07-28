"""Domain model classes for FODP (Flat OpenDocument Presentation).

Classes:
    FodpDocument — typed wrapper over the dict-based neutral model from load()

spec_qname: office:document
spec_fact_ref: see shared/qname-registry/fodp.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class FodpDocument:
    """Typed domain model for a Flat OpenDocument Presentation (.fodp) file.

    Wraps the neutral model dict returned by fodp_codec.load().
    Neutral model keys: is_fodp (bool), page_count (int),
    pages (list[dict]), styles_count (int).
    """

    spec_qname: ClassVar[str] = "office:document"
    spec_fact_ref: ClassVar[str] = "SAL-FODP-00001"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name: ClassVar[str] = "document"
    facade_names: ClassVar[list] = []

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str | Path) -> "FodpDocument":
        """Load a FODP file and return a FodpDocument."""
        from .fodp_codec import load
        return cls(load(path))

    @property
    def page_count(self) -> int:
        """Number of presentation slides."""
        return int(self._data.get("page_count", 0))

    @property
    def styles_count(self) -> int:
        """Number of defined styles."""
        return int(self._data.get("styles_count", 0))

    @property
    def pages(self) -> list[dict[str, Any]]:
        """List of slide dicts (name, style, title, text_content, shape_count)."""
        return list(self._data.get("pages", []))

    @property
    def is_fodp(self) -> bool:
        """True if the file was recognised as a valid FODP document."""
        return bool(self._data.get("is_fodp", False))

    # Presentation dimension properties (SAL-FODP-00001)
    @property
    def is_empty(self) -> bool:
        """True if the presentation has no slides."""
        return self.page_count == 0

    @property
    def is_single_page(self) -> bool:
        """True if the presentation has exactly one slide."""
        return self.page_count == 1

    @property
    def is_multi_page(self) -> bool:
        """True if the presentation has more than one slide."""
        return self.page_count > 1

    # Additional presentation analysis properties (SAL-FODP-00001)

    @property
    def has_styles(self) -> bool:
        """True if the presentation has at least one defined style."""
        return self.styles_count > 0

    @property
    def total_shape_count(self) -> int:
        """Total number of shapes across all slides."""
        return sum(p.get("shape_count", 0) for p in self.pages)

    @property
    def avg_shapes_per_slide(self) -> float:
        """Average number of shapes per slide. Returns 0.0 if no slides."""
        if self.page_count == 0:
            return 0.0
        return self.total_shape_count / self.page_count

    # Shape-based content analysis properties (SAL-FODP-00001)

    @property
    def has_shapes(self) -> bool:
        """True if the presentation contains at least one shape across all slides."""
        return self.total_shape_count > 0

    @property
    def is_shape_heavy(self) -> bool:
        """True if the average number of shapes per slide exceeds 5."""
        return self.avg_shapes_per_slide > 5

    @property
    def is_single_slide_with_shapes(self) -> bool:
        """True if the presentation has exactly one slide and at least one shape."""
        return self.page_count == 1 and self.total_shape_count > 0

    # Scale and content classification properties (SAL-FODP-00001 R1247)

    @property
    def is_large(self) -> bool:
        """True if page_count > 20."""
        return self.page_count > 20

    @property
    def has_titles(self) -> bool:
        """True if any slide has a non-empty, non-whitespace title."""
        return any(p.get("title", "").strip() for p in self.pages)

    @property
    def max_shapes_on_slide(self) -> int:
        """Maximum shape_count on any slide; 0 if no slides."""
        pages = self.pages
        if not pages:
            return 0
        return max(p.get("shape_count", 0) for p in pages)

    # Slide shape distribution properties (SAL-FODP-00001 R1267)

    @property
    def min_shapes_on_slide(self) -> int:
        """Minimum shape_count on any slide; 0 if no slides."""
        pages = self.pages
        if not pages:
            return 0
        return min(p.get("shape_count", 0) for p in pages)

    @property
    def slide_shape_range(self) -> int:
        """max_shapes_on_slide - min_shapes_on_slide; 0 if no slides."""
        pages = self.pages
        if not pages:
            return 0
        counts = [p.get("shape_count", 0) for p in pages]
        return max(counts) - min(counts)

    @property
    def has_uniform_slides(self) -> bool:
        """True if all slides have the same shape count."""
        pages = self.pages
        if not pages:
            return True
        counts = [p.get("shape_count", 0) for p in pages]
        return len(set(counts)) == 1

    def to_dict(self) -> dict[str, Any]:
        """Return document summary as a dict."""
        return {
            "is_fodp": self.is_fodp,
            "page_count": self.page_count,
            "styles_count": self.styles_count,
        }

    def __repr__(self) -> str:
        return f"FodpDocument(page_count={self.page_count}, styles_count={self.styles_count})"
