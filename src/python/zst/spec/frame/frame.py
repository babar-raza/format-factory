"""
ZST structural element: zst:frame

Spec ref: RFC 8878 — Zstandard Compression — Frame format
Fact ref: FACT-ZST-001
QName: zst:frame
Canonical class: Frame
Facade: ZstFrame
"""
from __future__ import annotations
from typing import Any, ClassVar


class Frame:
    """Canonical spec-shaped class for zst:frame (Zstandard frame)."""

    spec_qname: ClassVar[str] = "zst:frame"
    spec_fact_ref: ClassVar[str] = "FACT-ZST-001"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:8878:zstd"
    local_name: ClassVar[str] = "frame"
    facade_names: ClassVar[list] = ["ZstFrame"]

    MAGIC = 0xFD2FB528

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def frame_type(self) -> str:
        """Return the frame type string ('zstandard' or 'skippable')."""
        return str(self._data.get("frame_type", "zstandard"))

    @property
    def content_size(self) -> int:
        """Return the uncompressed content size in bytes (-1 if unknown)."""
        return int(self._data.get("content_size", -1))

    @property
    def checksum_flag(self) -> bool:
        """Return True if a content checksum is present in this frame."""
        return bool(self._data.get("checksum_flag", False))

    @property
    def block_count(self) -> int:
        """Return the number of compressed blocks in this frame."""
        return int(self._data.get("block_count", 0))

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying frame data dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Frame(type={self.frame_type!r}, content_size={self.content_size})"
