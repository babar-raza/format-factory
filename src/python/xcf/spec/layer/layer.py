"""
XCF structural element: xcf:layer

Spec ref: GIMP XCF file format — layer record
Fact ref: FACT-XCF-002
QName: xcf:layer
Canonical class: Layer
Facade: XcfLayer
"""
from __future__ import annotations
from typing import Any


class Layer:
    """Canonical spec-shaped class for xcf:layer."""

    spec_qname = "xcf:layer"
    spec_fact_ref = "FACT-XCF-002"
    namespace_uri = "urn:format:gimp:xcf:1.0"
    local_name = "layer"
    facade_names = ["XcfLayer"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def name(self) -> str:
        return str(self._data.get("name", ""))

    @property
    def width(self) -> int:
        return int(self._data.get("width", 0))

    @property
    def height(self) -> int:
        return int(self._data.get("height", 0))

    @property
    def type(self) -> int:
        return int(self._data.get("type", 0))

    @property
    def visible(self) -> bool:
        return bool(self._data.get("visible", True))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Layer(name={self.name!r}, width={self.width}, height={self.height})"
