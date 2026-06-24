"""
QOI structural element: qoi:end-marker

Spec ref: QOI format — end marker (8 zero bytes)
Fact ref: FACT-QOI-003
QName: qoi:end-marker
Canonical class: EndMarker
Facade: QoiEndMarker
"""
from __future__ import annotations
from typing import Any


class EndMarker:
    """Canonical spec-shaped class for qoi:end-marker."""

    spec_qname = "qoi:end-marker"
    spec_fact_ref = "FACT-QOI-003"
    namespace_uri = "urn:format:qoi:1.0"
    local_name = "end-marker"
    facade_names = ["QoiEndMarker"]

    # QOI end marker is 7 zero bytes followed by 0x01
    MARKER_BYTES = b"\x00" * 7 + b"\x01"

    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self._data = data or {}

    @property
    def offset(self) -> int:
        return int(self._data.get("offset", 0))

    @property
    def is_valid(self) -> bool:
        raw = self._data.get("raw_bytes", self.MARKER_BYTES)
        return raw == self.MARKER_BYTES

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"EndMarker(offset={self.offset}, valid={self.is_valid})"
