"""
PPM structural element: ppm:header

Spec ref: Netpbm format — PPM (Portable Pixmap) header
Fact ref: FACT-PPM-001
QName: ppm:header
Canonical class: Header
Facade: PpmHeader
"""
from __future__ import annotations
from typing import Any


class Header:
    """Canonical spec-shaped class for ppm:header."""

    spec_qname = "ppm:header"
    spec_fact_ref = "FACT-PPM-001"
    namespace_uri = "urn:format:netpbm:ppm:1.0"
    local_name = "header"
    facade_names = ["PpmHeader"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def magic(self) -> str:
        return str(self._data.get("magic", "P3"))

    @property
    def width(self) -> int:
        return int(self._data.get("width", 0))

    @property
    def height(self) -> int:
        return int(self._data.get("height", 0))

    @property
    def maxval(self) -> int:
        return int(self._data.get("maxval", 255))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(magic={self.magic!r}, width={self.width}, height={self.height}, maxval={self.maxval})"
