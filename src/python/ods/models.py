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
        return self._cell.value

    @property
    def value_type(self) -> str:
        return self._cell.value_type

    @property
    def text(self) -> str:
        return self._cell.text

    def to_dict(self) -> dict[str, Any]:
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
        return self._sheet.name

    @property
    def row_count(self) -> int:
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
