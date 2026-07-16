"""
MaterialX structural element: materialx:propertyset

Spec ref: Academy Software Foundation MaterialX Specification v1.39
Fact ref: FACT-MTLX-101 (write-path preserves all element kinds, incl. propertyset)
QName: materialx:propertyset
Canonical class: PropertySet
Facade: MtlxPropertySet
"""
from __future__ import annotations
from typing import Any


class PropertySet:
    """Canonical spec-shaped class for materialx:propertyset (a <propertyset>
    element, containing <property> children)."""

    spec_qname = "materialx:propertyset"
    spec_fact_ref = "FACT-MTLX-101"
    namespace_uri = "urn:format:materialx:1.39"
    local_name = "propertyset"
    facade_names = ["MtlxPropertySet"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def name(self) -> str:
        """Return the propertyset's ``name`` attribute value."""
        return str(self._data.get("name", ""))

    @property
    def properties(self) -> list[dict[str, Any]]:
        """Return nested <property> child elements captured verbatim."""
        return [c for c in self._data.get("children", []) if c.get("tag") == "property"]

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"PropertySet(name={self.name!r}, properties={len(self.properties)})"
