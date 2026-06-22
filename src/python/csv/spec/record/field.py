"""
CSV structural element: csv:field

Spec ref: RFC 4180 §2 — field definition
Fact ref: FACT-CSV-002
QName: csv:field
Canonical class: Field
Facade: CsvField
"""
from __future__ import annotations


class Field:
    """Canonical spec-shaped class for csv:field (RFC 4180 field value)."""

    spec_qname = "csv:field"
    spec_fact_ref = "FACT-CSV-002"
    namespace_uri = "urn:ietf:rfc:4180:csv"
    local_name = "field"
    facade_names = ["CsvField"]

    def __init__(self, value: str) -> None:
        self._value = str(value)

    @property
    def value(self) -> str:
        return self._value

    def is_empty(self) -> bool:
        return self._value == ""

    def is_quoted(self) -> bool:
        return self._value.startswith('"') and self._value.endswith('"')

    def __repr__(self) -> str:
        return f"Field({self._value!r})"
