"""
TSV structural element: tsv:field

Spec ref: IANA text/tab-separated-values — field value
Fact ref: SAL-TSV-00002
QName: tsv:field
Canonical class: Field
Facade: TsvField
"""
from __future__ import annotations
from typing import ClassVar


class Field:
    """Canonical spec-shaped class for tsv:field."""

    spec_qname: ClassVar[str] = "tsv:field"
    spec_fact_ref: ClassVar[str] = "SAL-TSV-00002"
    namespace_uri: ClassVar[str] = "urn:iana:media-type:text:tab-separated-values"
    local_name: ClassVar[str] = "field"
    facade_names: ClassVar[list] = ["TsvField"]

    def __init__(self, value: str) -> None:
        self._value = str(value)

    @property
    def value(self) -> str:
        return self._value

    def is_empty(self) -> bool:
        return self._value == ""

    def __repr__(self) -> str:
        return f"Field({self._value!r})"
