"""
SafeTensors structural element: safetensors:header

Spec ref: Hugging Face SafeTensors Specification v0.4 — File format
Fact ref: FACT-SAFETENSORS-001
QName: safetensors:header
Canonical class: Header
Facade: SafetensorsHeader
"""
from __future__ import annotations
from typing import Any


class Header:
    """Canonical spec-shaped class for safetensors:header (8-byte length + JSON header)."""

    spec_qname = "safetensors:header"
    spec_fact_ref = "FACT-SAFETENSORS-001"
    namespace_uri = "urn:format:safetensors:0.4"
    local_name = "header"
    facade_names = ["SafetensorsHeader"]

    HEADER_LEN_SIZE = 8

    def __init__(self, data: dict[str, Any]) -> None:
        """Wrap a parsed safetensors model dict (header_size/tensors/metadata)."""
        self._data = data

    @property
    def header_size(self) -> int:
        """Return the JSON header length in bytes (FACT-SAFETENSORS-001)."""
        return int(self._data.get("header_size", 0))

    @property
    def metadata(self) -> dict[str, str]:
        """Return the optional `__metadata__` string-to-string dict."""
        return dict(self._data.get("metadata", {}))

    @property
    def tensor_count(self) -> int:
        """Return the number of tensor descriptors present in the header."""
        return len(self._data.get("tensors", {}))

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(header_size={self.header_size}, tensor_count={self.tensor_count})"
