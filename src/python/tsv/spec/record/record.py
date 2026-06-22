"""
TSV structural element: tsv:record

Spec ref: IANA text/tab-separated-values media type
Fact ref: FACT-TSV-001
QName: tsv:record
Canonical class: Record
Facade: TsvRecord
"""
from __future__ import annotations


class Record:
    """Canonical spec-shaped class for tsv:record (TSV row)."""

    spec_qname = "tsv:record"
    spec_fact_ref = "FACT-TSV-001"
    namespace_uri = "urn:iana:media-type:text:tab-separated-values"
    local_name = "record"
    facade_names = ["TsvRecord"]

    def __init__(self, fields: list[str]) -> None:
        self._fields = list(fields)

    @property
    def fields(self) -> list[str]:
        return list(self._fields)

    @property
    def field_count(self) -> int:
        return len(self._fields)

    def get(self, index: int) -> str:
        if 0 <= index < len(self._fields):
            return self._fields[index]
        return ""

    def to_list(self) -> list[str]:
        return list(self._fields)

    def __repr__(self) -> str:
        return f"Record(field_count={self.field_count})"
