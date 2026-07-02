"""Domain classes for FODS — thin wrappers over the dict-based neutral model.

Classes:
    FodsDocument — wraps the workbook dict from parse_fods()
    FodsSheet — wraps a sheet dict
    FodsCell — wraps a cell dict

These preserve the existing function API while providing a class-based interface.
"""

from __future__ import annotations

from typing import Any, Iterator


class FodsCell:
    """Wraps a cell dict from the FODS neutral model."""

    spec_qname = "table:table-cell"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def value(self) -> Any:
        return self._data.get("value")

    @property
    def value_type(self) -> str:
        return self._data.get("value_type", "")

    @property
    def text(self) -> str:
        return self._data.get("text", "")

    @property
    def formula(self) -> str | None:
        return self._data.get("formula")

    @property
    def repeated(self) -> int:
        return self._data.get("repeated", 1)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"FodsCell(type={self.value_type!r}, value={self.value!r})"


class FodsSheet:
    """Wraps a sheet dict from the FODS neutral model."""

    spec_qname = "table:table"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @property
    def name(self) -> str:
        return self._data.get("name", "")

    @property
    def rows(self) -> list[list[dict[str, Any]]]:
        return self._data.get("rows", [])

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def cells(self) -> Iterator[FodsCell]:
        """Iterate all cells in the sheet."""
        for row in self.rows:
            row_cells = row.get("cells", []) if isinstance(row, dict) else row
            for cell_data in row_cells:
                yield FodsCell(cell_data)

    def cell_at(self, row: int, col: int) -> FodsCell | None:
        """Get cell at (row, col) or None if out of bounds."""
        if 0 <= row < len(self.rows) and 0 <= col < len(self.rows[row]):
            return FodsCell(self.rows[row][col])
        return None

    def find_cells_by_value(self, value: Any) -> list[FodsCell]:
        """Find all cells whose value matches the given value."""
        return [c for c in self.cells() if c.value == value]

    def iter_rows(self) -> Iterator[list[FodsCell]]:
        """Iterate rows, yielding each as a list of typed FodsCell objects."""
        for row in self.rows:
            row_cells = row.get("cells", []) if isinstance(row, dict) else row
            yield [FodsCell(c) for c in row_cells]

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"FodsSheet(name={self.name!r}, rows={self.row_count})"


class FodsDocument:
    """Wraps a workbook dict from parse_fods() with a class-based interface."""

    spec_qname = "office:document"

    def __init__(self, data: dict[str, Any]):
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> FodsDocument:
        """Parse a FODS file and wrap the result."""
        from .parser import parse_fods
        return cls(parse_fods(path))

    @property
    def format_id(self) -> str:
        return self._data.get("format_id", "fods")

    @property
    def odf_version(self) -> str:
        return self._data.get("odf_version", "")

    @property
    def sheet_count(self) -> int:
        return len(self._data.get("sheets", []))

    @property
    def warnings(self) -> list[dict[str, Any]]:
        return self._data.get("warnings", [])

    def sheets(self) -> list[FodsSheet]:
        """Return all sheets as FodsSheet objects."""
        return [FodsSheet(s) for s in self._data.get("sheets", [])]

    def sheet_by_name(self, name: str) -> FodsSheet | None:
        """Find a sheet by name."""
        for s in self._data.get("sheets", []):
            if s.get("name") == name:
                return FodsSheet(s)
        return None

    def find_sheet_by_index(self, index: int) -> FodsSheet | None:
        """Get sheet by zero-based index, or None if out of range."""
        sheets = self._data.get("sheets", [])
        if 0 <= index < len(sheets):
            return FodsSheet(sheets[index])
        return None

    # Workbook dimension properties (FACT-FODS-001)
    @property
    def is_empty(self) -> bool:
        """True if the workbook has no sheets."""
        return self.sheet_count == 0

    @property
    def is_single_sheet(self) -> bool:
        """True if the workbook has exactly one sheet."""
        return self.sheet_count == 1

    @property
    def is_multi_sheet(self) -> bool:
        """True if the workbook has more than one sheet."""
        return self.sheet_count > 1

    # Additional workbook analysis properties (FACT-FODS-001, FACT-FODS-002)

    @property
    def has_sheets(self) -> bool:
        """True if the workbook contains at least one sheet."""
        return self.sheet_count > 0

    @property
    def total_row_count(self) -> int:
        """Total number of rows across all sheets."""
        return sum(s.row_count for s in self.sheets())

    @property
    def max_sheet_rows(self) -> int:
        """Maximum row count in any single sheet. Returns 0 if no sheets."""
        counts = [s.row_count for s in self.sheets()]
        return max(counts) if counts else 0

    # Workbook scale properties (FACT-FODS-001 R1245)

    @property
    def is_large_workbook(self) -> bool:
        """True if total_row_count > 10000."""
        return self.total_row_count > 10000

    @property
    def has_many_sheets(self) -> bool:
        """True if sheet_count > 5."""
        return self.sheet_count > 5

    @property
    def avg_rows_per_sheet(self) -> float:
        """total_row_count / sheet_count; 0.0 if no sheets."""
        if self.sheet_count == 0:
            return 0.0
        return self.total_row_count / self.sheet_count

    # Sheet distribution properties (FACT-FODS-001 R1265)

    @property
    def min_sheet_rows(self) -> int:
        """Minimum row count in any sheet; 0 if no sheets."""
        counts = [s.row_count for s in self.sheets()]
        return min(counts) if counts else 0

    @property
    def sheet_row_range(self) -> int:
        """max_sheet_rows - min_sheet_rows; 0 if no sheets."""
        counts = [s.row_count for s in self.sheets()]
        if not counts:
            return 0
        return max(counts) - min(counts)

    @property
    def is_uniform_sheet_size(self) -> bool:
        """True if all sheets have the same row count."""
        counts = [s.row_count for s in self.sheets()]
        if not counts:
            return True
        return len(set(counts)) == 1

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying workbook dict."""
        return self._data

    def __repr__(self) -> str:
        return f"FodsDocument(sheets={self.sheet_count})"


# ---------------------------------------------------------------------------
# Cell-level accessor functions (gap-ledger closure)
# ---------------------------------------------------------------------------

def value_type(cell: dict[str, Any]) -> str:
    """Return the value type of a cell dict ('string', 'float', etc.)."""
    return cell.get("value_type", "")


def text(cell: dict[str, Any]) -> str:
    """Return the text/value content of a cell dict."""
    v = cell.get("value", cell.get("text", ""))
    return str(v) if v is not None else ""


def repeated(cell: dict[str, Any]) -> int:
    """Return the repeat count of a cell (default 1)."""
    return cell.get("repeated", cell.get("number_columns_repeated", 1))


# ---------------------------------------------------------------------------
# Workbook-level convenience functions (gap-ledger closure)
# ---------------------------------------------------------------------------

def from_file(file_path: "str | Any") -> dict[str, Any]:
    """Parse a FODS file and return the neutral model workbook dict."""
    from pathlib import Path as _P
    from .parser import parse_fods_strict
    return parse_fods_strict(_P(file_path))


def odf_version(workbook: dict[str, Any]) -> str:
    """Return the ODF version string from a parsed workbook."""
    return workbook.get("odf_version_attr", "")


def cell_at(workbook: dict[str, Any], sheet: "int | str", row: int, col: int) -> "dict[str, Any] | None":
    """Return the cell dict at (sheet, row, col), or None if not found."""
    sheets = workbook.get("sheets", [])
    target = None
    if isinstance(sheet, int):
        if 0 <= sheet < len(sheets):
            target = sheets[sheet]
    else:
        for s in sheets:
            if s.get("name") == sheet:
                target = s
                break
    if target is None:
        return None
    rows = target.get("rows", [])
    if row < 0 or row >= len(rows):
        return None
    cells = rows[row].get("cells", [])
    if col < 0 or col >= len(cells):
        return None
    return cells[col]


def to_dict(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-safe copy of the workbook dict (strips non-serializable fields)."""
    import copy
    result = copy.deepcopy(workbook)
    for key in list(result.keys()):
        if key.startswith("_"):
            del result[key]
    return result


def export_fods_to_csv(workbook: dict[str, Any], sheet: "int | str" = 0) -> str:
    """Export a single sheet from a parsed FODS workbook to CSV text."""
    import csv
    import io

    sheets = workbook.get("sheets", [])
    target = None
    if isinstance(sheet, int):
        if 0 <= sheet < len(sheets):
            target = sheets[sheet]
    else:
        for s in sheets:
            if s.get("name") == sheet:
                target = s
                break
    if target is None:
        return ""

    buf = io.StringIO()
    writer = csv.writer(buf)
    for row_data in target.get("rows", []):
        vals = []
        for cell in row_data.get("cells", []):
            v = cell.get("value")
            vals.append(str(v) if v is not None else "")
        writer.writerow(vals)
    return buf.getvalue()
