"""Domain model classes for DIF (Data Interchange Format).

Classes:
    DifDocument — typed wrapper over DifDocument from dif_parser

spec_qname: dif:document
spec_fact_ref: see shared/qname-registry/dif.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class DifModelDocument:
    """Typed domain model for a DIF spreadsheet document.

    Wraps the DifDocument dataclass returned by parse_dif_strict().
    Neutral model fields: title (str), vectors (int), tuples (int),
    rows (list[list[DifCell]]).
    """

    spec_qname: ClassVar[str] = "dif:document"
    spec_fact_ref: ClassVar[str] = "FACT-DIF-001"
    namespace_uri: ClassVar[str] = "urn:format:dif:1.0"
    local_name: ClassVar[str] = "document"
    facade_names: ClassVar[list] = []

    def __init__(self, parsed: Any) -> None:
        self._parsed = parsed

    @classmethod
    def from_file(cls, path: str | Path) -> "DifModelDocument":
        """Load a DIF file and return a DifModelDocument."""
        from .dif_parser import parse_dif_strict
        return cls(parse_dif_strict(path))

    @property
    def title(self) -> str:
        """Title header from the DIF file."""
        return str(self._parsed.title or "")

    @property
    def vectors(self) -> int:
        """Number of data columns (vectors)."""
        return int(self._parsed.vectors)

    @property
    def tuples(self) -> int:
        """Number of data rows (tuples)."""
        return int(self._parsed.tuples)

    @property
    def row_count(self) -> int:
        """Number of data rows parsed."""
        return len(self._parsed.rows)

    @property
    def cell_count(self) -> int:
        """Total number of cells across all rows."""
        return sum(len(row) for row in self._parsed.rows)

    # Document dimension properties (FACT-DIF-001)

    @property
    def col_count(self) -> int:
        """Number of data columns (alias for vectors)."""
        return self.vectors

    @property
    def is_empty(self) -> bool:
        """True if the document has no data rows."""
        return self.row_count == 0

    @property
    def is_single_row(self) -> bool:
        """True if the document has exactly one data row."""
        return self.row_count == 1

    def to_dict(self) -> dict[str, Any]:
        """Return document summary as a dict."""
        return {
            "title": self.title,
            "vectors": self.vectors,
            "tuples": self.tuples,
            "row_count": self.row_count,
            "cell_count": self.cell_count,
        }

    def __repr__(self) -> str:
        return (
            f"DifModelDocument(title={self.title!r}, "
            f"vectors={self.vectors}, tuples={self.tuples})"
        )


# Convenience alias
DifDoc = DifModelDocument
