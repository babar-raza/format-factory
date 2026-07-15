"""
XLIFF structural element: xliff:file

Spec ref: OASIS XLIFF 2.1 Specification — 2.1 The xliff Element
Fact ref: FACT-XLIFF-001
QName: xliff:file
Canonical class: File
Facade: XliffFile
"""
from __future__ import annotations
from typing import Any


class File:
    """Canonical spec-shaped class for xliff:file (a single translatable file)."""

    spec_qname = "xliff:file"
    spec_fact_ref = "FACT-XLIFF-001"
    namespace_uri = "urn:oasis:names:tc:xliff:document:2.0"
    local_name = "file"
    facade_names = ["XliffFile"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        """Return the file's ``id`` attribute value."""
        return str(self._data.get("id", ""))

    @property
    def units(self) -> list[dict[str, Any]]:
        """Return the list of translation-unit dicts contained in this file."""
        return self._data.get("units", [])

    @property
    def unit_count(self) -> int:
        """Return the number of translation units contained in this file."""
        return len(self.units)

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"File(id={self.id!r}, units={self.unit_count})"
