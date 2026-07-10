"""Domain model classes for ODS (OpenDocument Spreadsheet).

Classes:
    OdsModelDocument — typed wrapper over OdsDocument from ods_parser

spec_qname: office:document
spec_fact_ref: see shared/qname-registry/ods.yaml

Note: The name OdsModelDocument avoids collision with OdsDocument in ods_parser.py.
      Export alias OdsDoc is also provided for brevity.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Iterator


class OdsCellModel:
    """Typed wrapper for ODS cell."""

    spec_qname: ClassVar[str] = "table:table-cell"
    spec_fact_ref: ClassVar[str] = "FACT-ODS-003"

    def __init__(self, cell: Any) -> None:
        self._cell = cell

    @property
    def value(self) -> Any:
        """Return the cell value."""
        return self._cell.value

    @property
    def value_type(self) -> str:
        """Return the ODF value type string (e.g. 'string', 'float')."""
        return self._cell.value_type

    @property
    def text(self) -> str:
        """Return the display text content of the cell."""
        return self._cell.text

    def to_dict(self) -> dict[str, Any]:
        """Return a dict with value, value_type, and text keys."""
        return {"value": self.value, "value_type": self.value_type, "text": self.text}

    def __repr__(self) -> str:
        return f"OdsCellModel(type={self.value_type!r}, value={self.value!r})"


class OdsSheetModel:
    """Typed wrapper for ODS sheet with cell access."""

    spec_qname: ClassVar[str] = "table:table"
    spec_fact_ref: ClassVar[str] = "FACT-ODS-002"

    def __init__(self, sheet: Any) -> None:
        self._sheet = sheet

    @property
    def name(self) -> str:
        """Return the sheet name."""
        return self._sheet.name

    @property
    def row_count(self) -> int:
        """Return the number of rows in this sheet."""
        return len(self._sheet.rows)

    def cells(self) -> Iterator[OdsCellModel]:
        """Iterate all cells as OdsCellModel objects."""
        for row in self._sheet.rows:
            for cell in row.cells:
                yield OdsCellModel(cell)

    def cell_at(self, row: int, col: int) -> OdsCellModel | None:
        """Get cell at (row, col) or None."""
        if 0 <= row < len(self._sheet.rows):
            cells = self._sheet.rows[row].cells
            if 0 <= col < len(cells):
                return OdsCellModel(cells[col])
        return None

    def to_dict(self) -> dict[str, Any]:
        """Return a dict with name and row_count keys."""
        return {"name": self.name, "row_count": self.row_count}

    def __repr__(self) -> str:
        return f"OdsSheetModel(name={self.name!r}, rows={self.row_count})"


class OdsModelDocument:
    """Typed domain model for an OpenDocument Spreadsheet (.ods) file.

    Wraps the OdsDocument dataclass returned by parse_ods_strict().
    Neutral model fields: sheets (list[OdsSheet]), path (str).
    """

    spec_qname: ClassVar[str] = "office:document"
    spec_fact_ref: ClassVar[str] = "FACT-ODS-001"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name: ClassVar[str] = "document"
    facade_names: ClassVar[list] = []

    def __init__(self, parsed: Any) -> None:
        self._parsed = parsed

    @classmethod
    def from_file(cls, path: str | Path) -> "OdsModelDocument":
        """Load an ODS file and return an OdsModelDocument."""
        from .ods_parser import parse_ods_strict
        return cls(parse_ods_strict(path))

    @property
    def sheet_count(self) -> int:
        """Number of sheets in the spreadsheet."""
        return len(self._parsed.sheets)

    @property
    def sheet_names(self) -> list[str]:
        """Names of all sheets."""
        return [s.name for s in self._parsed.sheets]

    @property
    def path(self) -> str:
        """Path to the source ODS file."""
        return str(self._parsed.path)

    def get_sheet(self, index: int) -> OdsSheetModel | None:
        """Return typed OdsSheetModel at index, or None."""
        if 0 <= index < len(self._parsed.sheets):
            return OdsSheetModel(self._parsed.sheets[index])
        return None

    def sheets(self) -> list[OdsSheetModel]:
        """Return all sheets as typed OdsSheetModel objects."""
        return [OdsSheetModel(s) for s in self._parsed.sheets]

    # Workbook dimension properties (FACT-ODS-001)
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

    @property
    def has_sheets(self) -> bool:
        """True if the workbook has at least one sheet."""
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

    # Workbook scale properties (FACT-ODS-001 R1236)

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

    # Workbook density and shape properties (FACT-ODS-001 R1256)

    @property
    def is_uniform_sheet_size(self) -> bool:
        """True if all sheets have the same row count."""
        counts = [s.row_count for s in self.sheets()]
        if not counts:
            return True
        return len(set(counts)) == 1

    @property
    def min_sheet_rows(self) -> int:
        """Minimum row count in any single sheet; 0 if no sheets."""
        counts = [s.row_count for s in self.sheets()]
        return min(counts) if counts else 0

    @property
    def sheet_row_range(self) -> int:
        """max_sheet_rows - min_sheet_rows; 0 if no sheets."""
        sheets = self.sheets()
        if not sheets:
            return 0
        counts = [s.row_count for s in sheets]
        return max(counts) - min(counts)

    # Workbook structure analysis properties (FACT-ODS-001 R1276)

    @property
    def has_data_sheets(self) -> bool:
        """True if at least one sheet has rows."""
        return any(s.row_count > 0 for s in self.sheets())

    @property
    def largest_sheet_fraction(self) -> float:
        """max_sheet_rows / total_row_count; 0.0 if no rows."""
        total = self.total_row_count
        if total == 0:
            return 0.0
        return self.max_sheet_rows / total

    @property
    def is_single_sheet_dominant(self) -> bool:
        """True if largest_sheet_fraction > 0.8."""
        return self.largest_sheet_fraction > 0.8

    def set_cell_value(
        self,
        sheet_index: int,
        row: int,
        col: int,
        value: Any,
        value_type: str = "string",
    ) -> None:
        """Set a cell value in place, mutating this document.

        Delegates to ods_writer.set_cell_value(); extends rows/cells as needed.

        Raises:
            OdsError: If sheet_index is out of range.
        """
        from .ods_parser import OdsError
        from .ods_writer import set_cell_value as _set_cell_value
        success, msg = _set_cell_value(
            self._parsed, sheet_index, row, col, value, value_type
        )
        if not success:
            raise OdsError(msg)

    def save_to_file(self, path: "str | Path") -> None:
        """Save this document to an .ods file.

        Raises:
            OdsError: If path is empty or write fails.
        """
        from pathlib import Path as _Path
        from .ods_parser import OdsError
        from .ods_writer import write_ods
        if not path:
            raise OdsError("path must not be empty")
        dest = _Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        write_ods(self._parsed, dest)

    def to_dict(self) -> dict[str, Any]:
        """Return document summary as a dict."""
        return {
            "sheet_count": self.sheet_count,
            "sheet_names": self.sheet_names,
            "path": self.path,
        }

    def __repr__(self) -> str:
        return f"OdsModelDocument(sheet_count={self.sheet_count}, path={self.path!r})"


# Convenience alias
OdsDoc = OdsModelDocument
