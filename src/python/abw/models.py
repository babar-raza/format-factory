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

    # Document dimension properties (FACT-ABW-001)

    @property
    def is_empty(self) -> bool:
        """True if the document has no paragraphs."""
        return self.paragraph_count == 0

    @property
    def has_content(self) -> bool:
        """True if the document has at least one paragraph."""
        return self.paragraph_count > 0

    @property
    def is_single_paragraph(self) -> bool:
        """True if the document has exactly one paragraph."""
        return self.paragraph_count == 1

    @property
    def has_sections(self) -> bool:
        """True if the document contains at least one section."""
        return self.section_count > 0

    @property
    def has_multiple_paragraphs(self) -> bool:
        """True if the document contains more than one paragraph."""
        return self.paragraph_count > 1

    @property
    def is_multi_section(self) -> bool:
        """True if the document contains more than one section."""
        return self.section_count > 1

    # Text content analysis properties (FACT-ABW-001 R1229)

    @property
    def total_text_length(self) -> int:
        """Sum of character lengths of all paragraphs."""
        return sum(len(p) for p in self.paragraphs)

    @property
    def avg_paragraph_length(self) -> float:
        """Average characters per paragraph; 0.0 if no paragraphs."""
        if self.paragraph_count == 0:
            return 0.0
        return self.total_text_length / self.paragraph_count

    @property
    def has_long_paragraphs(self) -> bool:
        """True if any paragraph exceeds 200 characters."""
        return any(len(p) > 200 for p in self.paragraphs)

    # Scale and density properties (FACT-ABW-001 R1251)

    @property
    def is_large(self) -> bool:
        """True if paragraph_count > 50."""
        return self.paragraph_count > 50

    @property
    def is_text_heavy(self) -> bool:
        """True if total_text_length > 5000."""
        return self.total_text_length > 5000

    @property
    def paragraphs_per_section(self) -> float:
        """paragraph_count / section_count; 0.0 if no sections."""
        if self.section_count == 0:
            return 0.0
        return self.paragraph_count / self.section_count

    # Content balance properties (FACT-ABW-001 R1271)

    @property
    def avg_section_length(self) -> float:
        """total_text_length / section_count; 0.0 if no sections."""
        if self.section_count == 0:
            return 0.0
        return self.total_text_length / self.section_count

    @property
    def is_dense_text(self) -> bool:
        """True if avg_paragraph_length > 200."""
        return self.avg_paragraph_length > 200

    @property
    def is_sparse_text(self) -> bool:
        """True if avg_paragraph_length < 50 and paragraph_count > 0."""
        return self.paragraph_count > 0 and self.avg_paragraph_length < 50

    # Document structure properties (FACT-ABW-001 R1287)

    @property
    def is_moderate_text(self) -> bool:
        """True if 50 <= avg_paragraph_length <= 200."""
        return 50 <= self.avg_paragraph_length <= 200

    @property
    def has_rich_sections(self) -> bool:
        """True if paragraphs_per_section > 5."""
        return self.paragraphs_per_section > 5

    @property
    def is_long_document(self) -> bool:
        """True if total_text_length > 10000."""
        return self.total_text_length > 10000

    def add_paragraph(self, text: str) -> None:
        """Append a paragraph to this document in place.

        Mutates the internal paragraphs list and increments paragraph_count.

        Raises:
            AbwError: If text is None.
        """
        from .abw_codec import AbwError
        if text is None:
            raise AbwError("text must not be None")
        paras = self._data.setdefault("paragraphs", [])
        paras.append(str(text))
        self._data["paragraph_count"] = len(paras)

    def save_to_file(self, path: "str | Path") -> None:
        """Save this document to an .abw file (UTF-8 XML).

        Raises:
            AbwError: If path is empty or write fails.
        """
        from .abw_codec import AbwError, write_abw
        if not path:
            raise AbwError("path must not be empty")
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        write_abw(self._data, dest)

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying neutral model dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return (
            f"AbwDocument(section_count={self.section_count}, "
            f"paragraph_count={self.paragraph_count})"
        )
