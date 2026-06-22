"""
ZST structural element: zst:frame

Spec ref: RFC 8878 — Zstandard Compression — Frame format
Fact ref: FACT-ZST-001
QName: zst:frame
Canonical class: Frame
Facade: ZstFrame
"""
from __future__ import annotations
from typing import Any


class Frame:
    """Canonical spec-shaped class for zst:frame (Zstandard frame)."""

    spec_qname = "zst:frame"
    spec_fact_ref = "FACT-ZST-001"
    namespace_uri = "urn:ietf:rfc:8878:zstd"
    local_name = "frame"
    facade_names = ["ZstFrame"]

    MAGIC = 0xFD2FB528

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def frame_type(self) -> str:
        return str(self._data.get("frame_type", "zstandard"))

    @property
    def content_size(self) -> int:
        return int(self._data.get("content_size", -1))

    @property
    def checksum_flag(self) -> bool:
        return bool(self._data.get("checksum_flag", False))

    @property
    def block_count(self) -> int:
        return int(self._data.get("block_count", 0))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Frame(type={self.frame_type!r}, content_size={self.content_size})"
