"""
MaterialX structural element: materialx:typedef

Spec ref: Academy Software Foundation MaterialX Specification v1.39
Fact ref: FACT-MTLX-101 (write-path preserves all element kinds, incl. typedef)
QName: materialx:typedef
Canonical class: TypeDef
Facade: MtlxTypeDef
"""
from __future__ import annotations
from typing import Any


class TypeDef:
    """Canonical spec-shaped class for materialx:typedef (a <typedef> element)."""

    spec_qname = "materialx:typedef"
    spec_fact_ref = "FACT-MTLX-101"
    namespace_uri = "urn:format:materialx:1.39"
    local_name = "typedef"
    facade_names = ["MtlxTypeDef"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def name(self) -> str:
        """Return the typedef's ``name`` attribute value."""
        return str(self._data.get("name", ""))

    @property
    def children(self) -> list[dict[str, Any]]:
        """Return nested <member> (or other) child elements captured verbatim."""
        return list(self._data.get("children", []))

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"TypeDef(name={self.name!r})"
