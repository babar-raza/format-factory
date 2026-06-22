"""
TOML structural element: toml:key

Spec ref: TOML v1.0.0 — Keys
Fact ref: FACT-TOML-002
QName: toml:key
Canonical class: Key
Facade: TomlKey
"""
from __future__ import annotations
from typing import Any


class Key:
    """Canonical spec-shaped class for toml:key."""

    spec_qname = "toml:key"
    spec_fact_ref = "FACT-TOML-002"
    namespace_uri = "urn:format:toml:1.0"
    local_name = "key"
    facade_names = ["TomlKey"]

    def __init__(self, name: str, value: Any) -> None:
        self._name = name
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Any:
        return self._value

    @property
    def value_type(self) -> str:
        return type(self._value).__name__

    def to_dict(self) -> dict[str, Any]:
        return {"name": self._name, "value": self._value, "value_type": self.value_type}

    def __repr__(self) -> str:
        return f"Key(name={self._name!r}, value={self._value!r})"
