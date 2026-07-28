from __future__ import annotations
from typing import Any, ClassVar


class ListItem:
    """Canonical spec-shaped class for text:list-item in FODT context (ODF §5.3.1)."""

    spec_qname: ClassVar[str] = "text:list-item"
    spec_fact_ref: ClassVar[str] = "SAL-FODT-00005"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def text(self) -> str:
        return self._data.get("text", "")

    @property
    def spans(self) -> list:
        return self._data.get("spans", [])

    @property
    def level(self) -> int:
        return self._data.get("level", 1)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)
