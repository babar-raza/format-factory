"""FODG spec Page — canonical implementation of draw:page.

spec_qname: draw:page
spec_fact_ref: SAL-FODG-00414
Spec ref: ODF 1.3 §9.1.4
Facade: FodgPage (Compat/fodg_page.py)
"""
from __future__ import annotations

from typing import Any, ClassVar


class Page:
    """Canonical implementation of draw:page element for FODG.

    Wraps a page dict from the neutral model's 'pages' list.
    Typical keys: name (str), shape_count (int), shapes (list[dict]).
    """

    spec_qname: ClassVar[str] = "draw:page"
    spec_fact_ref: ClassVar[str] = "SAL-FODG-00414"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    local_name: ClassVar[str] = "page"
    facade_names: ClassVar[list] = ["FodgPage"]

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def shape_count(self) -> int:
        return int(self._data.get("shape_count", 0))

    @property
    def shapes(self) -> list[dict[str, Any]]:
        return list(self._data.get("shapes", []))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Page(name={self.name!r}, shape_count={self.shape_count})"
