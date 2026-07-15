"""
NRRD structural element: nrrd:header

Spec ref: Teem NRRD Format Specification — Section 2. Header
Fact ref: FACT-NRRD-002
QName: nrrd:header
Canonical class: Header
Facade: NrrdHeader
"""
from __future__ import annotations
from typing import Any


class Header:
    """Canonical spec-shaped class for nrrd:header (key:value header fields).

    Wraps the parsed header dict (type, dimension, sizes, encoding, endian)
    produced by ``nrrd.nrrd_codec.load_nrrd``. architecture_only marker class:
    no I/O, no parsing logic — a read-only view over an already-parsed dict.
    """

    spec_qname = "nrrd:header"
    spec_fact_ref = "FACT-NRRD-002"
    namespace_uri = "urn:format:nrrd:5.0"
    local_name = "header"
    facade_names = ["NrrdHeader"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def type(self) -> str:
        """Return the NRRD data type field (e.g. 'uint8', 'float', 'double')."""
        return str(self._data.get("type", ""))

    @property
    def dimension(self) -> int:
        """Return the number of array dimensions."""
        raw = self._data.get("dimension", "0")
        try:
            return int(raw)
        except (TypeError, ValueError):
            return 0

    @property
    def sizes(self) -> list[int]:
        """Return the per-axis sizes as a list of ints (empty if absent)."""
        sizes_str = self._data.get("sizes", "")
        if not sizes_str:
            return []
        return [int(s) for s in sizes_str.split()]

    @property
    def encoding(self) -> str:
        """Return the data encoding field (defaults to 'raw' per spec)."""
        return str(self._data.get("encoding", "raw"))

    @property
    def endian(self) -> str:
        """Return the endianness field ('little' or 'big'), empty if absent."""
        return str(self._data.get("endian", ""))

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying header dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(type={self.type!r}, dimension={self.dimension}, encoding={self.encoding!r})"
