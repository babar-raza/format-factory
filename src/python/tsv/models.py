"""Domain model classes for TSV (Tab-Separated Values).

Classes:
    TsvDocument — typed wrapper over the dict-based neutral model from parse_tsv_strict()

spec_qname: tsv:record
spec_fact_ref: see shared/qname-registry/tsv.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar


class TsvDocument:
    """Typed domain model for a TSV document.

    Wraps the neutral model dict returned by parse_tsv_strict().
    Neutral model keys: rows (list[list[str]]), headers (list[str]),
    row_count (int), has_header (bool), path (str).
    """

    spec_qname: ClassVar[str] = "tsv:record"
    spec_fact_ref: ClassVar[str] = "SAL-TSV-00001"
    namespace_uri: ClassVar[str] = "https://www.iana.org/assignments/media-types/text/tab-separated-values"
    local_name: ClassVar[str] = "record"
    facade_names: ClassVar[list] = []

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str | Path) -> "TsvDocument":
        """Load a TSV file and return a TsvDocument."""
        from .tsv_parser import parse_tsv_strict
        return cls(parse_tsv_strict(path))

    @property
    def headers(self) -> list[str]:
        """Column headers (first row if has_header, else empty list)."""
        return list(self._data.get("headers", []))

    @property
    def rows(self) -> list[list[str]]:
        """Data rows (excluding header row if present)."""
        return list(self._data.get("rows", []))

    @property
    def row_count(self) -> int:
        """Number of data rows (excludes header)."""
        return int(self._data.get("row_count", len(self.rows)))

    @property
    def has_header(self) -> bool:
        """True if the first row was detected as a header row."""
        return bool(self._data.get("has_header", False))

    @property
    def column_count(self) -> int:
        """Number of columns (from header or first row)."""
        if self.headers:
            return len(self.headers)
        rows = self.rows
        return len(rows[0]) if rows else 0

    def get_cell(self, row_index: int, col_index: int) -> str:
        """Return cell value at (row_index, col_index). Returns '' if out of bounds."""
        rows = self.rows
        if 0 <= row_index < len(rows):
            row = rows[row_index]
            if 0 <= col_index < len(row):
                return row[col_index]
        return ""

    def get_column_values(self, col_index: int) -> list[str]:
        """Return all data-row values in the given column.

        Args:
            col_index: Zero-based column index.

        Returns:
            list[str]: Values from each data row at col_index.
            Returns '' for rows that are shorter than col_index + 1.

        spec_qname: tsv:record
        spec_fact_ref: SAL-TSV-00001
        """
        return [row[col_index] if col_index < len(row) else "" for row in self.rows]

    # Tabular dimension properties (SAL-TSV-00001)

    @property
    def is_empty(self) -> bool:
        """True if the document has no data rows."""
        return self.row_count == 0

    @property
    def is_single_row(self) -> bool:
        """True if the document has exactly one data row."""
        return self.row_count == 1

    @property
    def is_wide(self) -> bool:
        """True if there are more columns than data rows."""
        return self.column_count > self.row_count

    @property
    def is_tall(self) -> bool:
        """True if there are more data rows than columns."""
        return self.row_count > self.column_count

    @property
    def is_multi_row(self) -> bool:
        """True if the document has more than one data row."""
        return self.row_count > 1

    @property
    def is_single_column(self) -> bool:
        """True if the document has exactly one column."""
        return self.column_count == 1

    @property
    def has_multiple_columns(self) -> bool:
        """True if the document has more than one column."""
        return self.column_count > 1

    # Additional tabular analysis properties (SAL-TSV-00001)

    @property
    def has_data(self) -> bool:
        """True if the document has at least one row and at least one column."""
        return self.row_count > 0 and self.column_count > 0

    @property
    def is_square(self) -> bool:
        """True if the number of rows equals the number of columns."""
        return self.row_count == self.column_count and self.row_count > 0

    @property
    def total_cell_count(self) -> int:
        """Total number of cells (row_count * column_count)."""
        return self.row_count * self.column_count

    # Scale classification properties (SAL-TSV-00001 R1234)

    @property
    def is_large(self) -> bool:
        """True if row_count > 10000."""
        return self.row_count > 10000

    @property
    def is_tiny(self) -> bool:
        """True if row_count <= 5."""
        return self.row_count <= 5

    @property
    def has_uniform_rows(self) -> bool:
        """True if all rows have column_count columns; True for empty docs."""
        rows = self.rows
        if not rows:
            return True
        expected = self.column_count
        return all(len(r) == expected for r in rows)

    # Density and shape properties (SAL-TSV-00001 R1254)

    @property
    def fill_density(self) -> float:
        """Fraction of non-empty cells; 0.0 if no cells."""
        total = self.total_cell_count
        if total == 0:
            return 0.0
        non_empty = sum(1 for row in self.rows for cell in row if cell != "")
        return non_empty / total

    @property
    def has_empty_cells(self) -> bool:
        """True if any cell in rows is an empty string."""
        return any(cell == "" for row in self.rows for cell in row)

    @property
    def aspect_ratio(self) -> float:
        """column_count / row_count; 0.0 if no rows."""
        if self.row_count == 0:
            return 0.0
        return self.column_count / self.row_count

    # Extended grid analysis properties (SAL-TSV-00001 R1274)

    @property
    def is_narrow_grid(self) -> bool:
        """True if row_count > 3 * column_count and column_count > 0."""
        return self.column_count > 0 and self.row_count > 3 * self.column_count

    @property
    def is_flat_grid(self) -> bool:
        """True if column_count > 3 * row_count and row_count > 0."""
        return self.row_count > 0 and self.column_count > 3 * self.row_count

    @property
    def is_sparse_data(self) -> bool:
        """True if fill_density < 0.5 and total_cell_count > 0."""
        return self.total_cell_count > 0 and self.fill_density < 0.5

    # Grid shape and fill completeness properties (SAL-TSV-00001 R1290)

    @property
    def is_square_grid(self) -> bool:
        """True if row_count == column_count and both positive."""
        return self.row_count > 0 and self.row_count == self.column_count

    @property
    def is_dense_data(self) -> bool:
        """True if fill_density > 0.8."""
        return self.fill_density > 0.8

    @property
    def empty_cell_count(self) -> int:
        """Number of empty cells: round((1 - fill_density) * total_cell_count)."""
        return round((1.0 - self.fill_density) * self.total_cell_count)

    def add_row(self, row: list[str]) -> None:
        """Append a data row to this document in place.

        Args:
            row: List of cell values to append as a new row.

        Raises:
            TsvError: If row is None.
        """
        from .exceptions import TsvError
        if row is None:
            raise TsvError("row must not be None")
        rows = self._data.setdefault("rows", [])
        rows.append([str(c) for c in row])
        self._data["row_count"] = len(rows)

    def set_cell(self, row_index: int, col_index: int, value: str) -> None:
        """Set a cell value in place, mutating this document.

        Args:
            row_index: Zero-based row index.
            col_index: Zero-based column index.
            value: New cell value.

        Raises:
            TsvError: If row_index or col_index is out of range.
        """
        from .exceptions import TsvError
        rows = self._data.get("rows", [])
        if row_index < 0 or row_index >= len(rows):
            raise TsvError(f"row_index {row_index} out of range (0..{len(rows) - 1})")
        row = rows[row_index]
        if col_index < 0 or col_index >= len(row):
            raise TsvError(f"col_index {col_index} out of range (0..{len(row) - 1})")
        rows[row_index][col_index] = str(value)

    def save_to_file(self, path: "str | Path") -> None:
        """Save this document to a .tsv file.

        Raises:
            TsvError: If path is empty or write fails.
        """
        from .exceptions import TsvError
        from .tsv_parser import write_tsv
        if not path:
            raise TsvError("path must not be empty")
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        headers = self._data.get("headers") or None
        write_tsv(self._data.get("rows", []), dest, headers=headers)

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying neutral model dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return (
            f"TsvDocument(row_count={self.row_count}, "
            f"column_count={self.column_count}, "
            f"has_header={self.has_header})"
        )
