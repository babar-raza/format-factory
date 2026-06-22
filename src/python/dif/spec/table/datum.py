"""
DIF structural element: dif:datum

Spec ref: DIF specification — data value cell
Fact ref: FACT-DIF-003
QName: dif:datum
Canonical class: Datum
Facade: DifDatum
"""
from __future__ import annotations
from typing import Any


class Datum:
    """Canonical spec-shaped class for dif:datum (cell value)."""

    spec_qname = "dif:datum"
    spec_fact_ref = "FACT-DIF-003"
    namespace_uri = "urn:format:dif:1.0"
    local_name = "datum"
    facade_names = ["DifDatum"]

    def __init__(self, value: Any, indicator: str = "V") -> None:
        self._value = value
        self._indicator = indicator

    @property
    def value(self) -> Any:
        return self._value

    @property
    def indicator(self) -> str:
        return self._indicator

    def is_numeric(self) -> bool:
        return self._indicator == "V"

    def is_string(self) -> bool:
        return self._indicator == "S"

    def to_dict(self) -> dict[str, Any]:
        return {"value": self._value, "indicator": self._indicator}

    def __repr__(self) -> str:
        return f"Datum({self._value!r}, indicator={self._indicator!r})"
