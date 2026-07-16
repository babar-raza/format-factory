"""
PGM structural element: pgm:header

Spec ref: Netpbm format — PGM (Portable Graymap) header
Fact ref: SAL-PGM-00001
QName: pgm:header
Canonical class: Header
Facade: PgmHeader
"""
from __future__ import annotations
from typing import Any, ClassVar


class Header:
    """Canonical spec-shaped class for pgm:header."""

    spec_qname: ClassVar[str] = "pgm:header"
    spec_fact_ref: ClassVar[str] = "SAL-PGM-00001"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:pgm:1.0"
    local_name: ClassVar[str] = "header"
    facade_names: ClassVar[list] = ["PgmHeader"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def magic(self) -> str:
        return str(self._data.get("magic", "P2"))

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
