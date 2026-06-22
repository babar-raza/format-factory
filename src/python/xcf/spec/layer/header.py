"""
XCF structural element: xcf:header

Spec ref: GIMP XCF file format — file header
Fact ref: FACT-XCF-001
QName: xcf:header
Canonical class: Header
Facade: XcfHeader
"""
from __future__ import annotations
from typing import Any


class Header:
    """Canonical spec-shaped class for xcf:header (XCF file header)."""

    spec_qname = "xcf:header"
    spec_fact_ref = "FACT-XCF-001"
    namespace_uri = "urn:format:gimp:xcf:1.0"
    local_name = "header"
    facade_names = ["XcfHeader"]

    MAGIC = b"gimp xcf "

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def version(self) -> str:
        return str(self._data.get("version", ""))

    @property
    def width(self) -> int:
        return int(self._data.get("width", 0))

    @property
    def height(self) -> int:
        return int(self._data.get("height", 0))

    @property
    def color_mode(self) -> int:
        return int(self._data.get("color_mode", 0))

    @property
    def layer_count(self) -> int:
        return int(self._data.get("layer_count", 0))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(version={self.version!r}, width={self.width}, height={self.height}, layers={self.layer_count})"
