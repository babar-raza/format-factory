"""FODT spec Span — canonical implementation of text:span.

spec_qname: text:span
spec_fact_ref: FACT-FODT-006
"""
from __future__ import annotations
from typing import Any, ClassVar


class Span:
    """Canonical implementation of ODF text:span element."""

    spec_qname: ClassVar[str] = "text:span"
    spec_fact_ref: ClassVar[str] = "FACT-FODT-006"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def text(self) -> str:
        return self._data.get("text", "")

    @property
    def style_name(self) -> str:
        return self._data.get("style_name", "")

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Span(text={self.text!r})"
