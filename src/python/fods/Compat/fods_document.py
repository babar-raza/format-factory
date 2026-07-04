"""FodsDocument — Production facade for the FODS document root element.

Spec authority: office:document (FACT-FODS-001, ODF 1.3 §3.1)
Canonical spec class: src/python/fods/spec/office/document.py::Document
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsDocument])

TC-MACH-ARCH-004 (2026-06-21): facade created to satisfy Gate 11 P-ARCH-001.
TC-W1-FODS-PY-002: worksheets property added for Aspose-style navigation.
"""
from __future__ import annotations

from typing import Any

from src.python.fods.spec.office.document import Document as _SpecDocument
from .fods_worksheet_collection import FodsWorksheetCollection


class FodsDocument(_SpecDocument):
    """Aspose-style facade for office:document (spec_qname=office:document).

    Provides:
      - worksheets  → FodsWorksheetCollection (Aspose-style navigation)
      - spec_qname, spec_fact_ref for Gate 11 P-ARCH-001 traceability

    TC-W1-FODS-PY-002: full Worksheets navigation wired.
    """

    spec_qname = "office:document"
    spec_fact_ref = "FACT-FODS-001"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    def __init__(self, data: dict[str, Any] | None = None):
        super().__init__(data)

    @classmethod
    def from_file(cls, path: str) -> FodsDocument:
        """Parse a FODS file and return an Compat FodsDocument instance."""
        from src.python.fods.parser import parse_fods
        return cls(parse_fods(path))

    @property
    def worksheets(self) -> FodsWorksheetCollection:
        """Return the Aspose-style navigable worksheet collection."""
        return FodsWorksheetCollection(self._data.get("sheets", []))
