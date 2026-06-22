"""
QOI structural element: qoi:header

Spec ref: QOI — The "Quite OK Image" format specification
Fact ref: FACT-QOI-001
QName: qoi:header
Canonical class: Header
Facade: QoiHeader
"""
from __future__ import annotations
from typing import Any


class Header:
    """Canonical spec-shaped class for qoi:header (14-byte QOI header)."""

    spec_qname = "qoi:header"
    spec_fact_ref = "FACT-QOI-001"
    namespace_uri = "urn:format:qoi:1.0"
    local_name = "header"
    facade_names = ["QoiHeader"]

    MAGIC = b"qoif"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def width(self) -> int:
        return int(self._data.get("width", 0))

    @property
    def height(self) -> int:
        return int(self._data.get("height", 0))

    @property
    def channels(self) -> int:
        return int(self._data.get("channels", 4))

    @property
    def colorspace(self) -> int:
        return int(self._data.get("colorspace", 0))

    @property
    def pixel_count(self) -> int:
        return self.width * self.height

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(width={self.width}, height={self.height}, channels={self.channels})"
