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
        """Return all translation-unit dicts contained in this file.

        Includes units nested inside <group> wrappers, at any depth
        (FACT-XLIFF-104) — not just units that are direct children of
        <file>.
        """
        from xliff.xliff_codec import iter_file_units

        return list(iter_file_units(self._data))

    @property
    def unit_count(self) -> int:
        """Return the total number of translation units contained in this file."""
        return len(self.units)

    @property
    def notes(self) -> list[dict[str, Any]]:
        """Return notes attached directly to this file (FACT-XLIFF-103)."""
        return self._data.get("notes", [])

    @property
    def groups(self) -> list[dict[str, Any]]:
        """Return the list of group dicts directly nested in this file (FACT-XLIFF-104)."""
        return self._data.get("groups", [])

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"File(id={self.id!r}, units={self.unit_count})"
