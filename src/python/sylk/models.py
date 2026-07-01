"""Domain model classes for SYLK (Symbolic Link) spreadsheet format.

Classes:
    SylkDocument — typed wrapper over SylkDocument from sylk_parser

spec_qname: sylk:document
spec_fact_ref: see shared/qname-registry/sylk.yaml

Note: The name SylkDocument here is the models-layer class; the parser
      also defines SylkDocument as a dataclass. Access via models module
      is the canonical public API.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class SylkModelDocument:
    """Typed domain model for a SYLK spreadsheet file.

    Wraps the SylkDocument dataclass returned by parse_sylk_strict().
    Neutral model fields: cells (list[SylkCell]), rows (int),
    cols (int), path (str), id_line (str).
    """

    spec_qname: ClassVar[str] = "sylk:document"
    spec_fact_ref: ClassVar[str] = "FACT-SYLK-001"
    namespace_uri: ClassVar[str] = "urn:format:sylk:1.0"
    local_name: ClassVar[str] = "document"
    facade_names: ClassVar[list] = []

    def __init__(self, parsed: Any) -> None:
        self._parsed = parsed

    @classmethod
    def from_file(cls, path: str | Path) -> "SylkModelDocument":
        """Load a SYLK file and return a SylkModelDocument."""
        from .sylk_parser import parse_sylk_strict
        return cls(parse_sylk_strict(path))

    @property
    def row_count(self) -> int:
        """Number of data rows."""
        return int(self._parsed.rows)

    @property
    def col_count(self) -> int:
        """Number of data columns."""
        return int(self._parsed.cols)

    @property
    def cell_count(self) -> int:
        """Total number of populated cells."""
        return len(self._parsed.cells)

    @property
    def path(self) -> str:
        """Path to the source SYLK file."""
        return str(self._parsed.path)

    @property
    def id_line(self) -> str:
        """The ID;P line from the SYLK header."""
        return str(self._parsed.id_line or "")

    @property
    def cells(self) -> list[Any]:
        """List of SylkCell objects."""
        return list(self._parsed.cells)

    # Document dimension properties (FACT-SYLK-014, FACT-SYLK-003)

    @property
    def is_empty(self) -> bool:
        """True if the document has no populated cells."""
        return self.cell_count == 0

    @property
    def is_single_cell(self) -> bool:
        """True if the document has exactly one populated cell."""
        return self.cell_count == 1

    @property
    def is_wide(self) -> bool:
        """True if there are more columns than rows."""
        return self.col_count > self.row_count

    @property
    def is_tall(self) -> bool:
        """True if there are more rows than columns."""
        return self.row_count > self.col_count

    def to_dict(self) -> dict[str, Any]:
        """Return document summary as a dict."""
        return {
            "row_count": self.row_count,
            "col_count": self.col_count,
            "cell_count": self.cell_count,
            "path": self.path,
        }

    def __repr__(self) -> str:
        return (
            f"SylkModelDocument(row_count={self.row_count}, "
            f"col_count={self.col_count}, cell_count={self.cell_count})"
        )


# Convenience alias
SylkDoc = SylkModelDocument
