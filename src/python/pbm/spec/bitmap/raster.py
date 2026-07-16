"""
PBM structural element: pbm:raster

Spec ref: Netpbm format — PBM (Portable Bitmap) raster data
Fact ref: SAL-PBM-00002
QName: pbm:raster
Canonical class: Raster
Facade: PbmRaster
"""
from __future__ import annotations
from typing import Any, ClassVar


class Raster:
    """Canonical spec-shaped class for pbm:raster."""

    spec_qname: ClassVar[str] = "pbm:raster"
    spec_fact_ref: ClassVar[str] = "SAL-PBM-00002"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:pbm:1.0"
    local_name: ClassVar[str] = "raster"
    facade_names: ClassVar[list] = ["PbmRaster"]

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
