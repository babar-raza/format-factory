from __future__ import annotations
from typing import Any, ClassVar


class TableRow:
    """Canonical spec-shaped class for table:table-row in FODT context (ODF §9.4)."""

    spec_qname: ClassVar[str] = "table:table-row"
    spec_fact_ref: ClassVar[str] = "SAL-FODT-00007"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def cells(self) -> list:
        return self._data.get("cells", [])

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)
