"""FODT spec Paragraph — canonical implementation of text:p.

spec_qname: text:p
spec_fact_ref: SAL-FODT-00003
"""
from __future__ import annotations
from typing import Any, ClassVar

from .span import Span


class Paragraph:
    """Canonical implementation of ODF text:p element."""

    spec_qname: ClassVar[str] = "text:p"
    spec_fact_ref: ClassVar[str] = "SAL-FODT-00003"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def kind(self) -> str:
        return self._data.get("kind", "paragraph")

    @property
    def text(self) -> str:
        return self._data.get("text", "")

    @property
    def style_name(self) -> str:
        return self._data.get("style_name", "")

    @property
    def outline_level(self) -> int | None:
        return self._data.get("outline_level")

    @property
    def spans(self) -> list[Span]:
        return [Span(s) for s in self._data.get("spans", [])]

    def set_text(self, text: str) -> None:
        """Mutate the paragraph text in place (TC-PCL-005)."""
        self._data["text"] = str(text)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Paragraph(kind={self.kind!r}, text={self.text!r})"
