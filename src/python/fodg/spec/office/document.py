"""FODG spec Document — canonical implementation of office:document.

spec_qname: office:document
spec_fact_ref: FACT-FODG-EX-0029
Spec ref: ODF 1.3 §3.1
Facade: FodgDocument (Compat/fodg_document.py)
"""
from __future__ import annotations

from typing import Any


class Document:
    """Canonical implementation of office:document root element for FODG.

    Wraps the neutral model dict produced by fodg_codec.load():
        mime_type (str), is_fodg (bool), page_count (int),
        pages (list[dict]), shapes_total (int)
    """

    spec_qname = "office:document"
    spec_fact_ref = "FACT-FODG-EX-0029"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name = "document"
    facade_names = ["FodgDocument"]

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def mime_type(self) -> str:
        return self._data.get("mime_type", "")

    @property
    def is_fodg(self) -> bool:
        return bool(self._data.get("is_fodg", False))

    @property
    def page_count(self) -> int:
        return int(self._data.get("page_count", 0))

    @property
    def shapes_total(self) -> int:
        return int(self._data.get("shapes_total", 0))

    @property
    def pages(self) -> list[dict[str, Any]]:
        return list(self._data.get("pages", []))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Document(page_count={self.page_count}, shapes_total={self.shapes_total})"
