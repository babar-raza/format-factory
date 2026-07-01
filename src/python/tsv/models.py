"""Domain model classes for TSV (Tab-Separated Values).

Classes:
    TsvDocument — typed wrapper over the dict-based neutral model from parse_tsv_strict()

spec_qname: tsv:record
spec_fact_ref: see shared/qname-registry/tsv.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class TsvDocument:
    """Typed domain model for a TSV document.

    Wraps the neutral model dict returned by parse_tsv_strict().
    Neutral model keys: rows (list[list[str]]), headers (list[str]),
    row_count (int), has_header (bool), path (str).
    """

    spec_qname = "tsv:record"
    spec_fact_ref = "FACT-TSV-001"
    namespace_uri = "https://www.iana.org/assignments/media-types/text/tab-separated-values"
    local_name = "record"
    facade_names = []

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

    # Tabular dimension properties (FACT-TSV-001)

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

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying neutral model dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return (
            f"TsvDocument(row_count={self.row_count}, "
            f"column_count={self.column_count}, "
            f"has_header={self.has_header})"
        )
