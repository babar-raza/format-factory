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

    def to_dict(self) -> dict[str, Any]:
        """Return the underlying workbook dict."""
        return self._data

    def __repr__(self) -> str:
        return f"FodsDocument(sheets={self.sheet_count})"
