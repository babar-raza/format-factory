"""
PGM structural element: pgm:graymap

Spec ref: Netpbm format — PGM pixel data
Fact ref: FACT-PGM-002
QName: pgm:graymap
Canonical class: Graymap
Facade: PgmGraymap
"""
from __future__ import annotations
from typing import Any


class Graymap:
    """Canonical spec-shaped class for pgm:graymap (grayscale pixel data)."""

    spec_qname = "pgm:graymap"
    spec_fact_ref = "FACT-PGM-002"
    namespace_uri = "urn:format:netpbm:pgm:1.0"
    local_name = "graymap"
    facade_names = ["PgmGraymap"]

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
        return f"Graymap(width={self.width}, height={self.height})"
