"""
ZST structural element: zst:block

Spec ref: RFC 8878 — Zstandard Compression — Block format
Fact ref: FACT-ZST-002
QName: zst:block
Canonical class: Block
Facade: ZstBlock
"""
from __future__ import annotations
from typing import Any, ClassVar


class Block:
    """Canonical spec-shaped class for zst:block (Zstandard data block)."""

    spec_qname: ClassVar[str] = "zst:block"
    spec_fact_ref: ClassVar[str] = "FACT-ZST-002"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:8878:zstd"
    local_name: ClassVar[str] = "block"
    facade_names: ClassVar[list] = ["ZstBlock"]

    BLOCK_TYPES = ("Raw_Block", "RLE_Block", "Compressed_Block", "Reserved")

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def block_type(self) -> str:
        """Return the Zstandard block type string."""
        return str(self._data.get("block_type", ""))

    @property
    def block_size(self) -> int:
        """Return the block payload size in bytes."""
        return int(self._data.get("block_size", 0))

    @property
    def is_last(self) -> bool:
        """Return True if this is the last block in the frame."""
        return bool(self._data.get("is_last", False))

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying block data dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Block(type={self.block_type!r}, size={self.block_size})"
