"""
PBM structural element: pbm:bitmap

Spec ref: Netpbm format — PBM pixel data
Fact ref: FACT-PBM-002
QName: pbm:bitmap
Canonical class: Bitmap
Facade: PbmBitmap
"""
from __future__ import annotations
from typing import Any


class Bitmap:
    """Canonical spec-shaped class for pbm:bitmap (pixel data)."""

    spec_qname = "pbm:bitmap"
    spec_fact_ref = "FACT-PBM-002"
    namespace_uri = "urn:format:netpbm:pbm:1.0"
    local_name = "bitmap"
    facade_names = ["PbmBitmap"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def width(self) -> int:
        return int(self._data.get("width", 0))

    @property
    def height(self) -> int:
        return int(self._data.get("height", 0))

    @property
    def pixel_count(self) -> int:
        return self.width * self.height

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Bitmap(width={self.width}, height={self.height})"
