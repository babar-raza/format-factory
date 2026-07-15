"""
XLIFF structural element: xliff:segment

Spec ref: OASIS XLIFF 2.1 Specification — 2.3 Translation Units (segment)
Fact ref: FACT-XLIFF-002
QName: xliff:segment
Canonical class: Segment
Facade: XliffSegment
"""
from __future__ import annotations
from typing import Any


class Segment:
    """Canonical spec-shaped class for xliff:segment (source/target text pair)."""

    spec_qname = "xliff:segment"
    spec_fact_ref = "FACT-XLIFF-002"
    namespace_uri = "urn:oasis:names:tc:xliff:document:2.0"
    local_name = "segment"
    facade_names = ["XliffSegment"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def source(self) -> str:
        """Return the segment's source-language text."""
        return str(self._data.get("source", ""))

    @property
    def target(self) -> str:
        """Return the segment's target-language (translated) text."""
        return str(self._data.get("target", ""))

    @property
    def state(self) -> str:
        """Return the segment's ``state`` attribute value (e.g. translated, final)."""
        return str(self._data.get("state", ""))

    @property
    def is_translated(self) -> bool:
        """Return True if the segment has non-whitespace target text."""
        return bool(self.target.strip())

    @property
    def source_content(self) -> list[Any]:
        """Return the structured inline-content list for source text
        (FACT-XLIFF-101) — preserves pc/sc/ec/ph/mrk boundaries that
        `.source` (plain flattened text) discards."""
        return self._data.get("source_content", [])

    @property
    def target_content(self) -> list[Any]:
        """Return the structured inline-content list for target text
        (FACT-XLIFF-101) — preserves pc/sc/ec/ph/mrk boundaries that
        `.target` (plain flattened text) discards."""
        return self._data.get("target_content", [])

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Segment(source={self.source!r}, target={self.target!r})"
