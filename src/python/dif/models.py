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
    spec_fact_ref: ClassVar[str] = "SAL-DIF-00001"
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

    # Document dimension properties (SAL-DIF-00001)

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

    @property
    def is_single_col(self) -> bool:
        """True if the document has exactly one data column (vector)."""
        return self.vectors == 1

    @property
    def has_title(self) -> bool:
        """True if the document has a non-empty title."""
        return bool(self.title)

    @property
    def is_multi_row(self) -> bool:
        """True if the document has more than one data row."""
        return self.row_count > 1

    @property
    def is_wide(self) -> bool:
        """True if there are more columns (vectors) than rows."""
        return self.vectors > self.row_count

    @property
    def is_tall(self) -> bool:
        """True if there are more rows than columns (vectors)."""
        return self.row_count > self.vectors

    @property
    def is_tabular(self) -> bool:
        """True if the document has both rows and columns."""
        return self.row_count > 0 and self.vectors > 0

    # Scale and geometry properties (SAL-DIF-00001 R1249)

    @property
    def is_large(self) -> bool:
        """True if cell_count > 1000."""
        return self.cell_count > 1000

    @property
    def aspect_ratio(self) -> float:
        """vectors / row_count; 0.0 if no rows."""
        if self.row_count == 0:
            return 0.0
        return self.vectors / self.row_count

    @property
    def is_square(self) -> bool:
        """True if row_count == vectors and both are positive."""
        return self.row_count > 0 and self.row_count == self.vectors

    # Extended grid analysis properties (SAL-DIF-00001 R1269)

    @property
    def is_narrow(self) -> bool:
        """True if row_count > 3 * vectors and vectors > 0."""
        return self.vectors > 0 and self.row_count > 3 * self.vectors

    @property
    def is_flat(self) -> bool:
        """True if vectors > 3 * row_count and row_count > 0."""
        return self.row_count > 0 and self.vectors > 3 * self.row_count

    @property
    def cell_density_ratio(self) -> float:
        """cell_count / (row_count * vectors); 0.0 if grid is empty."""
        denom = self.row_count * self.vectors
        if denom == 0:
            return 0.0
        return self.cell_count / denom

    # Grid density properties (SAL-DIF-00001 R1285)

    @property
    def is_dense_grid(self) -> bool:
        """True if cell_density_ratio > 0.8."""
        return self.cell_density_ratio > 0.8

    @property
    def is_sparse_grid(self) -> bool:
        """True if is_tabular and cell_density_ratio < 0.2."""
        return self.is_tabular and self.cell_density_ratio < 0.2

    @property
    def fill_classification(self) -> str:
        """'empty' if no grid; 'sparse' if ratio < 0.2; 'partial' if < 0.8; 'dense' if >= 0.8."""
        if not self.is_tabular or self.cell_count == 0:
            return "empty"
        ratio = self.cell_density_ratio
        if ratio < 0.2:
            return "sparse"
        if ratio < 0.8:
            return "partial"
        return "dense"

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
