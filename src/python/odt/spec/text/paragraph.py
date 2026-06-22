"""
ODF spec element: text:p (ODT paragraph)

Spec ref: ODF 1.3 §5.1.3 — Paragraph
Fact ref: FACT-ODT-EX-0094
QName: text:p
Namespace: urn:oasis:names:tc:opendocument:xmlns:text:1.0
Canonical class: Paragraph
Facade: OdtParagraph
"""
from __future__ import annotations
from typing import Any


class Paragraph:
    """Canonical spec-shaped class for text:p in ODT context."""

    spec_qname = "text:p"
    spec_fact_ref = "FACT-ODT-EX-0094"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    local_name = "p"
    facade_names = ["OdtParagraph"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def text(self) -> str:
        return str(self._data.get("text", ""))

    @property
    def style(self) -> str:
        return str(self._data.get("style", ""))

    @property
    def word_count(self) -> int:
        return len(self.text.split()) if self.text.strip() else 0

    def is_empty(self) -> bool:
        return not self.text.strip()

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        preview = self.text[:40] + "..." if len(self.text) > 40 else self.text
        return f"Paragraph({preview!r})"
