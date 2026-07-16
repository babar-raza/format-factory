"""
MaterialX structural element: materialx:nodedef

Spec ref: Academy Software Foundation MaterialX Specification v1.39
Fact ref: FACT-MTLX-101 (write-path preserves all element kinds, incl. nodedef)
QName: materialx:nodedef
Canonical class: NodeDef
Facade: MtlxNodeDef
"""
from __future__ import annotations
from typing import Any, ClassVar


class NodeDef:
    """Canonical spec-shaped class for materialx:nodedef (a <nodedef> element).

    TC-S6P4-PROD-009 (select-6 Phase 4): nodedef, typedef, look, and
    propertyset are all captured/preserved through the same generic-element
    machinery (_parse_generic_element/_serialize_nodes in mtlx_codec.py,
    FACT-MTLX-101) -- this facade gives materialx:nodedef its own canonical
    class per the repo's spec-qname-to-class naming rule, wrapping the same
    underlying dict shape rather than duplicating parsing logic.
    """

    spec_qname: ClassVar[str] = "materialx:nodedef"
    spec_fact_ref: ClassVar[str] = "FACT-MTLX-101"
    namespace_uri: ClassVar[str] = "urn:format:materialx:1.39"
    local_name: ClassVar[str] = "nodedef"
    facade_names: ClassVar[list] = ["MtlxNodeDef"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def name(self) -> str:
        """Return the nodedef's ``name`` attribute value."""
        return str(self._data.get("name", ""))

    @property
    def node_category(self) -> str:
        """Return the ``node`` attribute (the function/category this nodedef declares)."""
        return str(self._data.get("node_category", ""))

    @property
    def declared_type(self) -> str:
        """Return the ``type`` attribute (this nodedef's declared output data type)."""
        return str(self._data.get("attributes", {}).get("type", ""))

    @property
    def inputs(self) -> list[dict[str, str]]:
        """Return the list of ``<input>`` child element dicts."""
        return list(self._data.get("inputs", []))

    @property
    def outputs(self) -> list[dict[str, str]]:
        """Return the list of ``<output>`` child element dicts."""
        return list(self._data.get("outputs", []))

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"NodeDef(name={self.name!r}, node_category={self.node_category!r})"
