"""
XLIFF structural element: xliff:unit

Spec ref: OASIS XLIFF 2.1 Specification — 2.3 Translation Units
Fact ref: FACT-XLIFF-002
QName: xliff:unit
Canonical class: Unit
Facade: XliffUnit
"""
from __future__ import annotations
from typing import Any


class Unit:
    """Canonical spec-shaped class for xliff:unit (a translation unit)."""

    spec_qname = "xliff:unit"
    spec_fact_ref = "FACT-XLIFF-002"
    namespace_uri = "urn:oasis:names:tc:xliff:document:2.0"
    local_name = "unit"
    facade_names = ["XliffUnit"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        """Return the unit's ``id`` attribute value."""
        return str(self._data.get("id", ""))

    @property
    def segments(self) -> list[dict[str, Any]]:
        """Return the list of segment dicts contained in this unit."""
        return self._data.get("segments", [])

    @property
    def segment_count(self) -> int:
        """Return the number of segments contained in this unit."""
        return len(self.segments)

    @property
    def notes(self) -> list[dict[str, Any]]:
        """Return notes attached to this unit (FACT-XLIFF-103)."""
        return self._data.get("notes", [])

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Unit(id={self.id!r}, segments={self.segment_count})"
