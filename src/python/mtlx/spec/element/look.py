"""
MaterialX structural element: materialx:look

Spec ref: Academy Software Foundation MaterialX Specification v1.39
Fact ref: FACT-MTLX-101 (write-path preserves all element kinds, incl. look)
QName: materialx:look
Canonical class: Look
Facade: MtlxLook
"""
from __future__ import annotations
from typing import Any, ClassVar


class Look:
    """Canonical spec-shaped class for materialx:look (a <look> element,
    containing <materialassign> children)."""

    spec_qname: ClassVar[str] = "materialx:look"
    spec_fact_ref: ClassVar[str] = "FACT-MTLX-101"
    namespace_uri: ClassVar[str] = "urn:format:materialx:1.39"
    local_name: ClassVar[str] = "look"
    facade_names: ClassVar[list] = ["MtlxLook"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def name(self) -> str:
        """Return the look's ``name`` attribute value."""
        return str(self._data.get("name", ""))

    @property
    def material_assigns(self) -> list[dict[str, Any]]:
        """Return nested <materialassign> child elements captured verbatim."""
        return [c for c in self._data.get("children", []) if c.get("tag") == "materialassign"]

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Look(name={self.name!r}, material_assigns={len(self.material_assigns)})"
