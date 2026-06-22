"""OdsDocument — production facade for office:document (ODS).

Spec authority: office:document
Fact ref: FACT-ODS-EX-0029
Canonical spec class: src/python/ods/spec/office/document.py::Document
"""
from __future__ import annotations

from ..spec.office.document import Document as _SpecDocument
from ..spec.table.table import Table as _Table


class OdsDocument(_SpecDocument):
    """Production facade for office:document (ODF Spreadsheet root element)."""

    spec_qname = "office:document"
    spec_fact_ref = "FACT-ODS-EX-0029"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    @classmethod
    def from_file(cls, path: str) -> "OdsDocument":
        """Parse an ODS file and return an OdsDocument facade."""
        from ..ods_parser import parse_ods
        result = parse_ods(path)
        return cls(result if isinstance(result, dict) else {"sheets": []})

    def sheet_objects(self) -> list[_Table]:
        """Return all sheets as Table objects."""
        return [_Table(s) for s in self._data.get("sheets", [])]
