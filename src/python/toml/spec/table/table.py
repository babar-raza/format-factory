"""
TOML structural element: toml:table

Spec ref: TOML v1.0.0 — Tables
Fact ref: FACT-TOML-001
QName: toml:table
Canonical class: Table
Facade: TomlTable
"""
from __future__ import annotations
from typing import Any


class Table:
    """Canonical spec-shaped class for toml:table."""

    spec_qname = "toml:table"
    spec_fact_ref = "FACT-TOML-001"
    namespace_uri = "urn:format:toml:1.0"
    local_name = "table"
    facade_names = ["TomlTable"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = dict(data)

    @property
    def keys(self) -> list[str]:
        return list(self._data.keys())

    @property
    def key_count(self) -> int:
        return len(self._data)

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Table(key_count={self.key_count})"
