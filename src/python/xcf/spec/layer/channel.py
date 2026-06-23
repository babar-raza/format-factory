"""
XCF structural element: xcf:channel

Spec ref: GIMP XCF file format — channel record
Fact ref: FACT-XCF-003
QName: xcf:channel
Canonical class: Channel
Facade: XcfChannel
"""
from __future__ import annotations
from typing import Any


class Channel:
    """Canonical spec-shaped class for xcf:channel."""

    spec_qname = "xcf:channel"
    spec_fact_ref = "FACT-XCF-003"
    namespace_uri = "urn:format:gimp:xcf:1.0"
    local_name = "channel"
    facade_names = ["XcfChannel"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def name(self) -> str:
        return str(self._data.get("name", ""))

    @property
    def width(self) -> int:
        return int(self._data.get("width", 0))

    @property
    def height(self) -> int:
        return int(self._data.get("height", 0))

    @property
    def visible(self) -> bool:
        return bool(self._data.get("visible", True))

    @property
    def opacity(self) -> int:
        return int(self._data.get("opacity", 255))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Channel(name={self.name!r}, width={self.width}, height={self.height})"
