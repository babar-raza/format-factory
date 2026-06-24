"""
PBM structural element: pbm:raster

Spec ref: Netpbm format — PBM (Portable Bitmap) raster data
Fact ref: FACT-PBM-002
QName: pbm:raster
Canonical class: Raster
Facade: PbmRaster
"""
from __future__ import annotations
from typing import Any


class Raster:
    """Canonical spec-shaped class for pbm:raster."""

    spec_qname = "pbm:raster"
    spec_fact_ref = "FACT-PBM-002"
    namespace_uri = "urn:format:netpbm:pbm:1.0"
    local_name = "raster"
    facade_names = ["PbmRaster"]

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

    @property
    def rows(self) -> list:
        return list(self._data.get("rows", []))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Raster(width={self.width}, height={self.height})"
