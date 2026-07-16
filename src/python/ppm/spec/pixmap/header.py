"""
PPM structural element: ppm:header

Spec ref: Netpbm format — PPM (Portable Pixmap) header
Fact ref: SAL-PPM-00001
QName: ppm:header
Canonical class: Header
Facade: PpmHeader
"""
from __future__ import annotations
from typing import Any, ClassVar


class Header:
    """Canonical spec-shaped class for ppm:header."""

    spec_qname: ClassVar[str] = "ppm:header"
    spec_fact_ref: ClassVar[str] = "SAL-PPM-00001"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:ppm:1.0"
    local_name: ClassVar[str] = "header"
    facade_names: ClassVar[list] = ["PpmHeader"]

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
