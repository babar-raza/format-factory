"""
PBM structural element: pbm:header

Spec ref: Netpbm format — PBM (Portable Bitmap) header
Fact ref: FACT-PBM-001
QName: pbm:header
Canonical class: Header
Facade: PbmHeader
"""
from __future__ import annotations
from typing import Any


class Header:
    """Canonical spec-shaped class for pbm:header."""

    spec_qname = "pbm:header"
    spec_fact_ref = "FACT-PBM-001"
    namespace_uri = "urn:format:netpbm:pbm:1.0"
    local_name = "header"
    facade_names = ["PbmHeader"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def magic(self) -> str:
        return str(self._data.get("magic", "P1"))

    @property
    def width(self) -> int:
        return int(self._data.get("width", 0))

    @property
    def height(self) -> int:
        return int(self._data.get("height", 0))

    @property
    def is_binary(self) -> bool:
        return self.magic == "P4"

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(magic={self.magic!r}, width={self.width}, height={self.height})"
