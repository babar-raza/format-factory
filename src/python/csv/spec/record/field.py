"""
CSV structural element: csv:field

Spec ref: RFC 4180 §2 — field definition
Fact ref: FACT-CSV-002
QName: csv:field
Canonical class: Field
Facade: CsvField
"""
from __future__ import annotations
from typing import ClassVar


class Field:
    """Canonical spec-shaped class for csv:field (RFC 4180 field value)."""

    spec_qname: ClassVar[str] = "csv:field"
    spec_fact_ref: ClassVar[str] = "FACT-CSV-002"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:4180:csv"
    local_name: ClassVar[str] = "field"
    facade_names: ClassVar[list] = ["CsvField"]

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
