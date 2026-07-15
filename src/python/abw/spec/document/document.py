"""ABW spec Document — canonical implementation of abw:abiword.

spec_qname: abw:abiword
spec_fact_ref: FACT-ABW-001
Spec ref: AbiWord AWML 1.0 — root document element
Facade: AbwDocument (Compat/abw_document.py)
"""
from __future__ import annotations

from typing import Any, ClassVar

from .paragraph import Paragraph


class Document:
    """Canonical implementation of the abw:abiword document root element.

    Wraps the neutral model dict produced by abw_codec.load().
    The neutral model keys are:
        is_abw (bool), section_count (int), paragraph_count (int), paragraphs (list[str])
    """

    spec_qname: ClassVar[str] = "abiword:document"
    spec_fact_ref: ClassVar[str] = "FACT-ABW-001"
    namespace_uri: ClassVar[str] = "http://www.abisource.com/awml/"
    local_name: ClassVar[str] = "abiword"
    facade_names: ClassVar[list] = ["AbwDocument"]

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def is_abw(self) -> bool:
        return bool(self._data.get("is_abw", False))

    @property
    def section_count(self) -> int:
        return int(self._data.get("section_count", 0))

    @property
    def paragraph_count(self) -> int:
        return int(self._data.get("paragraph_count", 0))

    @property
    def paragraphs(self) -> list[str]:
        return list(self._data.get("paragraphs", []))

    def paragraph_objects(self) -> list[Paragraph]:
        """Return all paragraphs as Paragraph objects."""
        return [Paragraph(text) for text in self._data.get("paragraphs", [])]

    def is_empty(self) -> bool:
        """Return True if the document has no non-whitespace paragraph content."""
        return all(not p.strip() for p in self._data.get("paragraphs", []))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return (
            f"Document(section_count={self.section_count}, "
            f"paragraph_count={self.paragraph_count})"
        )
