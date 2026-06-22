"""ABW spec Field — canonical implementation of abw:field.

spec_qname: abw:field
spec_fact_ref: FACT-ABW-005
Spec ref: AbiWord AWML 1.0 — field inline element
"""
from __future__ import annotations


class Field:
    """Canonical implementation of the abw:field element.

    A field represents dynamic content within a paragraph
    (e.g. page numbers, date, author name).
    """

    spec_qname = "abw:field"
    spec_fact_ref = "FACT-ABW-005"
    namespace_uri = "http://www.abisource.com/awml/"
    local_name = "field"
    facade_names = []

    def __init__(self, field_type: str, value: str = ""):
        self._field_type = str(field_type) if field_type else ""
        self._value = str(value) if value else ""

    @property
    def field_type(self) -> str:
        return self._field_type

    @property
    def value(self) -> str:
        return self._value

    def to_dict(self) -> dict:
        return {"field_type": self._field_type, "value": self._value}

    def __repr__(self) -> str:
        return f"Field(field_type={self._field_type!r}, value={self._value!r})"
