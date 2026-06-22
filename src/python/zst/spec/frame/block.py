"""
ZST structural element: zst:block

Spec ref: RFC 8878 — Zstandard Compression — Block format
Fact ref: FACT-ZST-002
QName: zst:block
Canonical class: Block
Facade: ZstBlock
"""
from __future__ import annotations
from typing import Any


class Block:
    """Canonical spec-shaped class for zst:block (Zstandard data block)."""

    spec_qname = "zst:block"
    spec_fact_ref = "FACT-ZST-002"
    namespace_uri = "urn:ietf:rfc:8878:zstd"
    local_name = "block"
    facade_names = ["ZstBlock"]

    BLOCK_TYPES = ("Raw_Block", "RLE_Block", "Compressed_Block", "Reserved")

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def block_type(self) -> str:
        return str(self._data.get("block_type", ""))

    @property
    def block_size(self) -> int:
        return int(self._data.get("block_size", 0))

    @property
    def is_last(self) -> bool:
        return bool(self._data.get("is_last", False))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Block(type={self.block_type!r}, size={self.block_size})"
