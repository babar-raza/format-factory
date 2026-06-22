"""
ODF spec element: office:document (ODS root element)

Spec ref: ODF 1.3 §3.1 — Document Root Element
Fact ref: FACT-ODS-EX-0029
QName: office:document
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Document
Facade: OdsDocument
"""
from __future__ import annotations
from typing import Any


class Document:
    """Canonical spec-shaped class for office:document in ODS context."""

    spec_qname = "office:document"
    spec_fact_ref = "FACT-ODS-EX-0029"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name = "document"
    facade_names = ["OdsDocument"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def sheet_count(self) -> int:
        return len(self._data.get("sheets", []))

    @property
    def sheets(self) -> list:
        return list(self._data.get("sheets", []))

    @property
    def is_ods(self) -> bool:
        return True

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Document(sheet_count={self.sheet_count})"
