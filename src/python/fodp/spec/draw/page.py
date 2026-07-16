"""
ODF spec element: draw:page (FODP presentation slide)

Spec ref: ODF 1.3 §9.1.4 — Drawing Page
Fact ref: SAL-FODP-00414
QName: draw:page
Namespace: urn:oasis:names:tc:opendocument:xmlns:drawing:1.0
Canonical class: Page
Facade: FodpPage
"""
from __future__ import annotations
from typing import Any, ClassVar


class Page:
    """Canonical spec-shaped class for draw:page in FODP context (presentation slide)."""

    spec_qname: ClassVar[str] = "presentation:page"
    spec_fact_ref: ClassVar[str] = "SAL-FODP-00414"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    local_name: ClassVar[str] = "page"
    facade_names: ClassVar[list] = ["FodpPage"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def name(self) -> str:
        return str(self._data.get("name", ""))

    @property
    def layout(self) -> str:
        return str(self._data.get("layout", ""))

    @property
    def shape_count(self) -> int:
        return int(self._data.get("shape_count", len(self._data.get("shapes", []))))

    @property
    def shapes(self) -> list:
        return list(self._data.get("shapes", []))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Page(name={self.name!r}, shape_count={self.shape_count})"
