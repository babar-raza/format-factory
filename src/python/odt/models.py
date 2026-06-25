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
    spec_fact_ref: ClassVar[str] = "FACT-ODT-001"
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
