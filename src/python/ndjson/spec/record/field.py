"""
NDJSON structural element: ndjson:field

Spec ref: NDJSON — key-value field within a record
Fact ref: FACT-NDJSON-002
QName: ndjson:field
Canonical class: Field
Facade: NdjsonField
"""
from __future__ import annotations
from typing import Any


class Field:
    """Canonical spec-shaped class for ndjson:field."""

    spec_qname = "ndjson:field"
    spec_fact_ref = "FACT-NDJSON-002"
    namespace_uri = "urn:format:ndjson:1.0"
    local_name = "field"
    facade_names = ["NdjsonField"]

    def __init__(self, key: str, value: Any) -> None:
        self._key = key
        self._value = value

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> Any:
        return self._value

    def is_null(self) -> bool:
        return self._value is None

    def to_dict(self) -> dict[str, Any]:
        return {"key": self._key, "value": self._value}

    def __repr__(self) -> str:
        return f"Field(key={self._key!r}, value={self._value!r})"
