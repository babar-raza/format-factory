from __future__ import annotations
from typing import Any, ClassVar


class List:
    """Canonical spec-shaped class for text:list in FODT context (ODF §5.3.1)."""

    spec_qname: ClassVar[str] = "text:list"
    spec_fact_ref: ClassVar[str] = "FACT-FODT-005"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def items(self) -> list:
        return self._data.get("items", [])

    @property
    def style_name(self) -> str:
        return self._data.get("style_name", "")

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)
