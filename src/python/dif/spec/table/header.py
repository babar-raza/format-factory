"""
DIF structural element: dif:header

Spec ref: DIF (Data Interchange Format) specification — header block
Fact ref: FACT-DIF-001
QName: dif:header
Canonical class: Header
Facade: DifHeader
"""
from __future__ import annotations
from typing import Any


class Header:
    """Canonical spec-shaped class for dif:header block."""

    spec_qname = "dif:header"
    spec_fact_ref = "FACT-DIF-001"
    namespace_uri = "urn:format:dif:1.0"
    local_name = "header"
    facade_names = ["DifHeader"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def rows(self) -> int:
        return int(self._data.get("rows", 0))

    @property
    def cols(self) -> int:
        return int(self._data.get("cols", 0))

    @property
    def format_version(self) -> str:
        return str(self._data.get("format_version", ""))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Header(rows={self.rows}, cols={self.cols})"
