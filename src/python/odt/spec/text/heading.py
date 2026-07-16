"""
ODF spec element: text:h (ODT heading)

Spec ref: ODF 1.3 §5.1.2 — Heading
Fact ref: SAL-ODT-00091
QName: text:h
Namespace: urn:oasis:names:tc:opendocument:xmlns:text:1.0
Canonical class: Heading
Facade: OdtHeading
"""
from __future__ import annotations
from typing import Any, ClassVar


class Heading:
    """Canonical spec-shaped class for text:h in ODT context."""

    spec_qname: ClassVar[str] = "text:h"
    spec_fact_ref: ClassVar[str] = "SAL-ODT-00091"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    local_name: ClassVar[str] = "h"
    facade_names: ClassVar[list] = ["OdtHeading"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def text(self) -> str:
        return str(self._data.get("text", ""))

    @property
    def level(self) -> int:
        return int(self._data.get("level", 1))

    def is_empty(self) -> bool:
        return not self.text.strip()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Heading(level={self.level}, text={self.text!r})"
