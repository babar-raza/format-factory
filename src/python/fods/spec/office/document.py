"""
ODF spec element: office:document

Spec ref: ODF 1.3 §3.1 — Document Element (flat format)
Fact ref: FACT-FODS-001
QName: office:document
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Office.Document
"""
from __future__ import annotations

from typing import Any, ClassVar


class Document:
    """Canonical spec-shaped class for office:document in FODS context.

    Root element of a flat ODS document. Contains office:body, office:automatic-styles,
    and office:scripts. Attributes include office:version and xmlns declarations.

    Facades in Compat/ should delegate to this class via spec_qname.
    """

    spec_qname: ClassVar[str] = "office:document"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-001"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name: ClassVar[str] = "document"
    facade_names: ClassVar[list] = ["FodsDocument"]

    def __init__(self, data: dict[str, Any] | None = None):
        self._data: dict[str, Any] = data or {}

    @property
    def format_id(self) -> str:
        return self._data.get("format_id", "fods")

    @property
    def odf_version(self) -> str:
        return self._data.get("odf_version", "")

    @property
    def sheet_count(self) -> int:
        return len(self._data.get("sheets", []))

    @property
    def warnings(self) -> list[dict[str, Any]]:
        return self._data.get("warnings", [])

    def has_sheets(self) -> bool:
        return self.sheet_count > 0

    def raw_sheets(self) -> list[dict[str, Any]]:
        return self._data.get("sheets", [])

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Document(sheets={self.sheet_count})"
