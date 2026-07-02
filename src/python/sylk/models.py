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

    # Cell type analysis properties (FACT-SYLK-008, FACT-SYLK-016)
    @property
    def numeric_cell_count(self) -> int:
        """Number of cells with numeric values."""
        return sum(1 for c in self._parsed.cells if c.value_type == "numeric")

    @property
    def string_cell_count(self) -> int:
        """Number of cells with string values."""
        return sum(1 for c in self._parsed.cells if c.value_type == "string")

    @property
    def nonempty_cell_count(self) -> int:
        """Number of cells with non-empty values (numeric or string)."""
        return sum(1 for c in self._parsed.cells if c.value_type != "empty")

    # Additional cell analysis properties (FACT-SYLK-001)

    @property
    def has_numeric_cells(self) -> bool:
        """True if the document contains at least one numeric cell."""
        return self.numeric_cell_count > 0

    @property
    def has_string_cells(self) -> bool:
        """True if the document contains at least one string cell."""
        return self.string_cell_count > 0

    @property
    def fill_ratio(self) -> float:
        """Ratio of non-empty cells to total cells. Returns 0.0 if no cells."""
        if self.cell_count == 0:
            return 0.0
        return self.nonempty_cell_count / self.cell_count

    # Grid density properties (FACT-SYLK-001 R1228)

    @property
    def is_dense(self) -> bool:
        """True if fill_ratio > 0.8."""
        return self.fill_ratio > 0.8

    @property
    def is_sparse(self) -> bool:
        """True if fill_ratio < 0.2."""
        return self.fill_ratio < 0.2

    @property
    def is_large_grid(self) -> bool:
        """True if cell_count > 1000."""
        return self.cell_count > 1000

    # Geometry and type composition properties (FACT-SYLK-001 R1250)

    @property
    def is_square(self) -> bool:
        """True if row_count == col_count and both positive."""
        return self.row_count > 0 and self.row_count == self.col_count

    @property
    def has_mixed_types(self) -> bool:
        """True if document contains both numeric and string cells."""
        return self.has_numeric_cells and self.has_string_cells

    @property
    def numeric_ratio(self) -> float:
        """numeric_cell_count / cell_count; 0.0 if no cells."""
        if self.cell_count == 0:
            return 0.0
        return self.numeric_cell_count / self.cell_count

    # Cell type distribution properties (FACT-SYLK-001 R1270)

    @property
    def string_ratio(self) -> float:
        """string_cell_count / cell_count; 0.0 if no cells."""
        if self.cell_count == 0:
            return 0.0
        return self.string_cell_count / self.cell_count

    @property
    def is_numeric_dominant(self) -> bool:
        """True if numeric_ratio > 0.5."""
        return self.numeric_ratio > 0.5

    @property
    def is_all_numeric(self) -> bool:
        """True if nonempty cells exist and all non-empty cells are numeric."""
        return self.nonempty_cell_count > 0 and self.numeric_cell_count == self.nonempty_cell_count

    # Cell type homogeneity properties (FACT-SYLK-001 R1286)

    @property
    def is_all_string(self) -> bool:
        """True if nonempty cells exist and all non-empty cells are string."""
        return self.nonempty_cell_count > 0 and self.string_cell_count == self.nonempty_cell_count

    @property
    def has_single_type(self) -> bool:
        """True if nonempty cells exist and all non-empty cells share one type."""
        return self.nonempty_cell_count > 0 and (self.is_all_numeric or self.is_all_string)

    @property
    def is_string_dominant(self) -> bool:
        """True if string_ratio > 0.5."""
        return self.string_ratio > 0.5

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
