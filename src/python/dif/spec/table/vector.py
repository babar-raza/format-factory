"""
DIF structural element: dif:vector

Spec ref: DIF specification — data vector
Fact ref: SAL-DIF-00002
QName: dif:vector
Canonical class: Vector
Facade: DifVector
"""
from __future__ import annotations
from typing import Any, ClassVar


class Vector:
    """Canonical spec-shaped class for dif:vector (row or column vector)."""

    spec_qname: ClassVar[str] = "dif:vector"
    spec_fact_ref: ClassVar[str] = "SAL-DIF-00002"
    namespace_uri: ClassVar[str] = "urn:format:dif:1.0"
    local_name: ClassVar[str] = "vector"
    facade_names: ClassVar[list] = ["DifVector"]

    def __init__(self, data: list[Any]) -> None:
        self._data = list(data)

    @property
    def items(self) -> list:
        return list(self._data)

    @property
    def length(self) -> int:
        return len(self._data)

    def to_list(self) -> list:
        return list(self._data)

    def __repr__(self) -> str:
        return f"Vector(length={self.length})"
