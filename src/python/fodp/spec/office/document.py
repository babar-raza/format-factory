"""
ODF spec element: office:document (FODP root element)

Spec ref: ODF 1.3 §3.1 — Document Root Element
Fact ref: FACT-FODP-EX-0029
QName: office:document
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Document
Facade: FodpDocument
"""
from __future__ import annotations
from typing import Any


class Document:
    """Canonical spec-shaped class for office:document in FODP context."""

    spec_qname = "office:document"
    spec_fact_ref = "FACT-FODP-EX-0029"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name = "document"
    facade_names = ["FodpDocument"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def mime_type(self) -> str:
        return self._data.get("mime_type", "application/vnd.oasis.opendocument.presentation")

    @property
    def is_fodp(self) -> bool:
        return bool(self._data.get("is_fodp", True))

    @property
    def page_count(self) -> int:
        return int(self._data.get("page_count", 0))

    @property
    def styles_count(self) -> int:
        return int(self._data.get("styles_count", 0))

    @property
    def pages(self) -> list:
        return list(self._data.get("pages", []))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Document(page_count={self.page_count})"
