"""FODT spec Heading — canonical implementation of text:h.

spec_qname: text:h
spec_fact_ref: FACT-FODT-004
"""
from __future__ import annotations
from typing import Any, ClassVar

from .span import Span


class Heading:
    """Canonical implementation of ODF text:h element."""

    spec_qname: ClassVar[str] = "text:h"
    spec_fact_ref: ClassVar[str] = "FACT-FODT-004"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def kind(self) -> str:
        return "heading"

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

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Heading(level={self.outline_level!r}, text={self.text!r})"
