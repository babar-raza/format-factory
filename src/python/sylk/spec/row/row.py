"""
SYLK structural element: sylk:row

Spec ref: SYLK format — R (row) record
Fact ref: SAL-SYLK-00002
QName: sylk:row
Canonical class: Row
Facade: SylkRow
"""
from __future__ import annotations
from typing import Any, ClassVar


class Row:
    """Canonical spec-shaped class for sylk:row."""

    spec_qname: ClassVar[str] = "sylk:row"
    spec_fact_ref: ClassVar[str] = "SAL-SYLK-00002"
    namespace_uri: ClassVar[str] = "urn:format:sylk:1.0"
    local_name: ClassVar[str] = "row"
    facade_names: ClassVar[list] = ["SylkRow"]

    def __init__(self, index: int, cells: list[Any]) -> None:
        self._index = index
        self._cells = list(cells)

    @property
    def index(self) -> int:
        return self._index

    @property
    def cells(self) -> list:
        return list(self._cells)

    @property
    def cell_count(self) -> int:
        return len(self._cells)

    def to_dict(self) -> dict[str, Any]:
        return {"index": self._index, "cells": self._cells}

    def __repr__(self) -> str:
        return f"Row(index={self._index}, cell_count={self.cell_count})"
