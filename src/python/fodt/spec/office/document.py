"""FODT spec Document — canonical implementation of office:document.

spec_qname: office:document
spec_fact_ref: FACT-FODT-001
Spec ref: ODF 1.3 §3.1 — Document Element (flat format)
Facade: FodtDocument (Compat/fodt_document.py)
"""
from __future__ import annotations

from typing import Any, ClassVar


class Document:
    """Canonical implementation of ODF office:document element for FODT.

    Root element of a flat ODF text document. Contains office:body with
    text:* content (paragraphs, headings, tables, lists).
    """

    spec_qname: ClassVar[str] = "office:document"
    spec_fact_ref: ClassVar[str] = "FACT-FODT-001"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name: ClassVar[str] = "document"
    facade_names: ClassVar[list] = ["FodtDocument"]

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def format_id(self) -> str:
        return self._data.get("format_id", "fodt")

    @property
    def odf_version(self) -> str:
        return self._data.get("odf_version", "")

    @property
    def block_count(self) -> int:
        return len(self._data.get("blocks", []))

    @property
    def table_count(self) -> int:
        return len(self._data.get("tables", []))

    @property
    def warnings(self) -> list[dict[str, Any]]:
        return self._data.get("warnings", [])

    def to_dict(self) -> dict[str, Any]:
        return self._data

    def __repr__(self) -> str:
        return f"Document(format_id={self.format_id!r}, blocks={self.block_count})"
