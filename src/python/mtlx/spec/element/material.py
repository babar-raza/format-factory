"""
MaterialX structural element: materialx:material

Spec ref: Academy Software Foundation MaterialX Specification v1.39
Fact ref: FACT-MTLX-003
QName: materialx:material
Canonical class: Material
Facade: MtlxMaterial
"""
from __future__ import annotations
from typing import Any, ClassVar


class Material:
    """Canonical spec-shaped class for materialx:material (a <surfacematerial> element)."""

    spec_qname: ClassVar[str] = "materialx:material"
    spec_fact_ref: ClassVar[str] = "FACT-MTLX-003"
    namespace_uri: ClassVar[str] = "urn:format:materialx:1.39"
    local_name: ClassVar[str] = "surfacematerial"
    facade_names: ClassVar[list] = ["MtlxMaterial"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def name(self) -> str:
        """Return the material's ``name`` attribute value."""
        return str(self._data.get("name", ""))

    @property
    def inputs(self) -> list[dict[str, str]]:
        """Return the list of ``<input>`` child element dicts."""
        return list(self._data.get("inputs", []))

    @property
    def input_count(self) -> int:
        """Return the number of ``<input>`` child elements."""
        return len(self.inputs)

    @property
    def has_surfaceshader_input(self) -> bool:
        """Return True if this material declares a surfaceshader input (connected or not)."""
        return any(inp.get("name") == "surfaceshader" for inp in self.inputs)

    @property
    def shader_nodename(self) -> str:
        """Return the nodename the surfaceshader input connects to, or '' if unconnected."""
        for inp in self.inputs:
            if inp.get("name") == "surfaceshader":
                return str(inp.get("nodename", ""))
        return ""

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Material(name={self.name!r}, inputs={self.input_count})"
