"""Domain model classes for ODT (OpenDocument Text).

Classes:
    OdtModelDocument — typed wrapper over OdtDocument from odt_parser

spec_qname: office:document
spec_fact_ref: see shared/qname-registry/odt.yaml

Note: The name OdtModelDocument avoids collision with OdtDocument in odt_parser.py.
      Export alias OdtDoc is also provided for brevity.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class OdtModelDocument:
    """Typed domain model for an OpenDocument Text (.odt) file.

    Wraps the OdtDocument dataclass returned by parse_odt_strict().
    Neutral model fields: paragraphs (list[OdtParagraph]),
    headings (list[OdtHeading]), elements (list), path (str).
    """

    spec_qname: ClassVar[str] = "office:document"
    spec_fact_ref: ClassVar[str] = "SAL-ODT-01067"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name: ClassVar[str] = "document"
    facade_names: ClassVar[list] = []

    def __init__(self, parsed: Any) -> None:
        self._parsed = parsed

    @classmethod
    def from_file(cls, path: str | Path) -> "OdtModelDocument":
        """Load an ODT file and return an OdtModelDocument."""
        from .odt_parser import parse_odt_strict
        return cls(parse_odt_strict(path))

    @property
    def paragraph_count(self) -> int:
        """Number of text paragraphs in the document."""
        return len(self._parsed.paragraphs)

    @property
    def heading_count(self) -> int:
        """Number of headings in the document."""
        return len(self._parsed.headings)

    @property
    def path(self) -> str:
        """Path to the source ODT file."""
        return str(self._parsed.path)

    @property
    def paragraphs(self) -> list[Any]:
        """List of OdtParagraph objects."""
        return list(self._parsed.paragraphs)

    @property
    def headings(self) -> list[Any]:
        """List of OdtHeading objects."""
        return list(self._parsed.headings)

    # Document dimension properties (SAL-ODT-01067)

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
    def has_headings(self) -> bool:
        """True if the document has at least one heading."""
        return self.heading_count > 0

    # Additional structural properties (SAL-ODT-01067)

    @property
    def is_multi_paragraph(self) -> bool:
        """True if the document has more than one paragraph."""
        return self.paragraph_count > 1

    @property
    def has_multiple_headings(self) -> bool:
        """True if the document has more than one heading."""
        return self.heading_count > 1

    @property
    def total_block_count(self) -> int:
        """Total number of text blocks (paragraphs + headings)."""
        return self.paragraph_count + self.heading_count

    # Document composition analysis properties (SAL-ODT-01067)

    @property
    def is_heading_heavy(self) -> bool:
        """True if headings outnumber paragraphs (heading_count > paragraph_count)."""
        return self.heading_count > self.paragraph_count

    @property
    def is_content_rich(self) -> bool:
        """True if the document has more than 10 total blocks (paragraphs + headings)."""
        return self.total_block_count > 10

    @property
    def heading_ratio(self) -> float:
        """Fraction of total blocks that are headings. Returns 0.0 if no blocks."""
        if self.total_block_count == 0:
            return 0.0
        return self.heading_count / self.total_block_count

    # Scale and content balance properties (SAL-ODT-01067 R1244)

    @property
    def is_large(self) -> bool:
        """True if total_block_count > 50."""
        return self.total_block_count > 50

    @property
    def has_only_paragraphs(self) -> bool:
        """True if paragraph_count > 0 and heading_count == 0."""
        return self.paragraph_count > 0 and self.heading_count == 0

    @property
    def paragraph_ratio(self) -> float:
        """paragraph_count / total_block_count; 0.0 if no blocks."""
        if self.total_block_count == 0:
            return 0.0
        return self.paragraph_count / self.total_block_count

    # Content balance and structure properties (SAL-ODT-01067 R1264)

    @property
    def is_outline_heavy(self) -> bool:
        """True if heading_ratio > 0.3."""
        return self.heading_ratio > 0.3

    @property
    def has_balanced_content(self) -> bool:
        """True if heading_ratio is in [0.1, 0.5]."""
        return 0.1 <= self.heading_ratio <= 0.5

    @property
    def is_prose_heavy(self) -> bool:
        """True if paragraph_ratio > 0.8."""
        return self.paragraph_ratio > 0.8

    def add_paragraph(self, text: str) -> None:
        """Append a paragraph to this document in place.

        Args:
            text: Paragraph text to append.

        Raises:
            OdtError: If text is None.
        """
        from .odt_parser import OdtError, OdtParagraph
        if text is None:
            raise OdtError("text must not be None")
        self._parsed.paragraphs.append(OdtParagraph(text=str(text)))

    def save_to_file(self, path: "str | Path") -> None:
        """Save this document to an .odt file.

        Extracts paragraph texts from the model and delegates to write_odt().

        Raises:
            OdtError: If path is empty or write fails.
        """
        from .odt_parser import OdtError
        from .odt_writer import write_odt
        if not path:
            raise OdtError("path must not be empty")
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        para_texts = [p.text for p in self._parsed.paragraphs]
        write_odt(para_texts, dest)

    def to_dict(self) -> dict[str, Any]:
        """Return document summary as a dict."""
        return {
            "paragraph_count": self.paragraph_count,
            "heading_count": self.heading_count,
            "path": self.path,
        }

    def __repr__(self) -> str:
        return (
            f"OdtModelDocument(paragraph_count={self.paragraph_count}, "
            f"heading_count={self.heading_count})"
        )


# Convenience alias
OdtDoc = OdtModelDocument
