# CANONICAL EXAMPLE — KC-PYTHON-001
# Copied from: src/python/csv/models.py at git HEAD 30de4ad0
# This file is the authoritative reference for the {Format}Document pattern.
# DO NOT EDIT — update src/python/csv/models.py and re-copy here when the contract changes.
# See .supervisor/knowledge/contracts/python-domain-model.yaml for the full contract.
"""Domain model classes for CSV (Comma-Separated Values).

Classes:
    CsvDocument — typed wrapper over the dict-based neutral model from parse_csv_strict()

spec_qname: csv:record
spec_fact_ref: see shared/qname-registry/csv.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class CsvDocument:
    """Typed domain model for a CSV document.

    Wraps the neutral model dict returned by parse_csv_strict().
    Neutral model keys: rows (list[list[str]]), headers (list[str]),
    row_count (int), has_header (bool), delimiter (str).
    """

    # REQUIRED: spec_qname class attribute (bare assignment — NOT ClassVar type hint)
    # Must match the qname field in shared/qname-registry/{format}.yaml exactly.
    spec_qname = "csv:record"
    # REQUIRED: spec_fact_ref class attribute
    spec_fact_ref = "FACT-CSV-001"
    # REQUIRED: namespace_uri class attribute
    namespace_uri = "https://www.iana.org/assignments/media-types/text/csv"
    # REQUIRED: local_name class attribute
    local_name = "record"
    # REQUIRED: facade_names class attribute
    facade_names = []

    def __init__(self, data: dict[str, Any]) -> None:
        # REQUIRED: stores neutral model as self._data (dict-based variant)
        # list-based variant (NDJSON): self._records = list(records)
        # path-based variant (ZST): self._path = Path(path); self._data = data or {}
        self._data = data

    # REQUIRED: from_file classmethod — relative import INSIDE method body
    @classmethod
    def from_file(cls, path: str | Path) -> "CsvDocument":
        """Load a CSV file and return a CsvDocument."""
        from .csv_parser import parse_csv_strict  # relative import inside method body
        return cls(parse_csv_strict(path))

    # REQUIRED: typed property methods — defensive copies, .get() with defaults, coerce type
    @property
    def headers(self) -> list[str]:
        """Column headers (first row if has_header, else empty list)."""
        return list(self._data.get("headers", []))  # defensive copy

    @property
    def rows(self) -> list[list[str]]:
        """Data rows (excluding header row if present)."""
        return list(self._data.get("rows", []))  # defensive copy

    @property
    def row_count(self) -> int:
        """Number of data rows (excludes header)."""
        return int(self._data.get("row_count", len(self.rows)))  # coerce to int

    @property
    def has_header(self) -> bool:
        """True if the first row was detected as a header row."""
        return bool(self._data.get("has_header", False))  # coerce to bool

    @property
    def delimiter(self) -> str:
        """Delimiter character used in the CSV (typically ',')."""
        return str(self._data.get("delimiter", ","))  # coerce to str

    @property
    def column_count(self) -> int:
        """Number of columns (from header or first row)."""
        if self.headers:
            return len(self.headers)
        rows = self.rows
        return len(rows[0]) if rows else 0

    # REQUIRED: accessor method — returns safe default on out-of-bounds
    def get_cell(self, row_index: int, col_index: int) -> str:
        """Return cell value at (row_index, col_index). Returns '' if out of bounds."""
        rows = self.rows
        if 0 <= row_index < len(rows):
            row = rows[row_index]
            if 0 <= col_index < len(row):
                return row[col_index]
        return ""  # safe default

    # REQUIRED: to_dict() (or to_list() for list-based variant) — round-trip export
    def to_dict(self) -> dict[str, Any]:
        """Return the underlying neutral model dict."""
        return dict(self._data)  # defensive copy

    # REQUIRED: __repr__ — includes key counts
    def __repr__(self) -> str:
        return (
            f"CsvDocument(row_count={self.row_count}, "
            f"column_count={self.column_count}, "
            f"has_header={self.has_header})"
        )

# REQUIRED: Export in __init__.py as:
#   from .models import CsvDocument  # noqa: F401
#
# REQUIRED: Tests at:
#   tests/python/csv_format/test_csv_document_model.py
