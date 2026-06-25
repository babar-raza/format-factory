"""Domain model classes for ABW (AbiWord).

Classes:
    AbwDocument — typed wrapper over the dict-based neutral model from load()

spec_qname: abiword:document
spec_fact_ref: see shared/qname-registry/abw.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class AbwDocument:
    """Typed domain model for an AbiWord (.abw) document.

    Wraps the neutral model dict returned by abw_codec.load().
    Neutral model keys: is_abw (bool), section_count (int),
    paragraph_count (int), paragraphs (list[str]).
    """

    spec_qname = "abiword:document"
    spec_fact_ref = "FACT-ABW-001"
    namespace_uri = "http://www.abisource.com/awml/"
    local_name = "document"
    facade_names = []

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str | Path) -> "AbwDocument":
        """Load an ABW file and return an AbwDocument."""
        from .abw_codec import load
        return cls(load(path))

    @property
    def section_count(self) -> int:
        """Number of <section> elements in the document."""
        return int(self._data.get("section_count", 0))

    @property
    def paragraph_count(self) -> int:
        """Number of <p> (paragraph) elements in the document."""
        return int(self._data.get("paragraph_count", 0))

    @property
    def paragraphs(self) -> list[str]:
        """Text content of each paragraph."""
        return list(self._data.get("paragraphs", []))

    @property
    def is_abw(self) -> bool:
        """True if the source was a valid AbiWord document."""
        return bool(self._data.get("is_abw", False))

    def get_paragraph(self, index: int) -> str:
        """Return paragraph text at index. Returns '' if out of bounds."""
        paras = self.paragraphs
        if 0 <= index < len(paras):
            return paras[index]
        return ""

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying neutral model dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return (
            f"AbwDocument(section_count={self.section_count}, "
            f"paragraph_count={self.paragraph_count})"
        )
