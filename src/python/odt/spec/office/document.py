"""
ODF spec element: office:document (ODT root element)

Spec ref: ODF 1.3 §3.1 — Document Root Element
Fact ref: SAL-ODT-00028
QName: office:document
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Document
Facade: OdtDocument
"""
from __future__ import annotations
from typing import Any, ClassVar


class Document:
    """Canonical spec-shaped class for office:document in ODT context."""

    spec_qname: ClassVar[str] = "office:document"
    spec_fact_ref: ClassVar[str] = "SAL-ODT-00028"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name: ClassVar[str] = "document"
    facade_names: ClassVar[list] = ["OdtDocument"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def paragraph_count(self) -> int:
        return int(self._data.get("paragraph_count", len(self._data.get("paragraphs", []))))

    @property
    def heading_count(self) -> int:
        return int(self._data.get("heading_count", len(self._data.get("headings", []))))

    @property
    def paragraphs(self) -> list:
        return list(self._data.get("paragraphs", []))

    @property
    def headings(self) -> list:
        return list(self._data.get("headings", []))

    @property
    def is_ok(self) -> bool:
        return bool(self._data.get("ok", True))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Document(paragraph_count={self.paragraph_count}, heading_count={self.heading_count})"
