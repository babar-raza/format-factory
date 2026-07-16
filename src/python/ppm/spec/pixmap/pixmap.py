"""
PPM structural element: ppm:pixmap

Spec ref: Netpbm format — PPM RGB pixel data
Fact ref: SAL-PPM-00002
QName: ppm:pixmap
Canonical class: Pixmap
Facade: PpmPixmap
"""
from __future__ import annotations
from typing import Any, ClassVar


class Pixmap:
    """Canonical spec-shaped class for ppm:pixmap (RGB pixel data)."""

    spec_qname: ClassVar[str] = "ppm:pixmap"
    spec_fact_ref: ClassVar[str] = "SAL-PPM-00002"
    namespace_uri: ClassVar[str] = "urn:format:netpbm:ppm:1.0"
    local_name: ClassVar[str] = "pixmap"
    facade_names: ClassVar[list] = ["PpmPixmap"]

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
        return f"Pixmap(width={self.width}, height={self.height})"
