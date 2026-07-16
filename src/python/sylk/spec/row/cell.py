"""
SYLK structural element: sylk:cell

Spec ref: SYLK format — C (cell) record
Fact ref: SAL-SYLK-00003
QName: sylk:cell
Canonical class: Cell
Facade: SylkCell
"""
from __future__ import annotations
from typing import Any, ClassVar


class Cell:
    """Canonical spec-shaped class for sylk:cell."""

    spec_qname: ClassVar[str] = "sylk:cell"
    spec_fact_ref: ClassVar[str] = "SAL-SYLK-00003"
    namespace_uri: ClassVar[str] = "urn:format:sylk:1.0"
    local_name: ClassVar[str] = "cell"
    facade_names: ClassVar[list] = ["SylkCell"]

    def __init__(self, row: int, col: int, value: Any) -> None:
        self._row = row
        self._col = col
        self._value = value

    @property
    def row(self) -> int:
        return self._row

    @property
    def col(self) -> int:
        return self._col

    @property
    def value(self) -> Any:
        return self._value

    def to_dict(self) -> dict[str, Any]:
        return {"row": self._row, "col": self._col, "value": self._value}

    def __repr__(self) -> str:
        return f"Cell(row={self._row}, col={self._col}, value={self._value!r})"
