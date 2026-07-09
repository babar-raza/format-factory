"""FodsWorksheetCollection — Aspose-style navigable worksheet collection.

Spec authority: office:spreadsheet (FACT-FODS-003, ODF 1.3 §9.1)
TC-W1-FODS-PY-002: Aspose-style deep navigation (FodsDocument → FodsWorksheetCollection).

API:
  doc.worksheets.count                  → int
  doc.worksheets[0]                     → FodsWorksheet by index
  doc.worksheets["Sheet1"]              → FodsWorksheet by name
  doc.worksheets.add("Sheet2")          → FodsWorksheet (new)
  doc.worksheets.remove("Sheet2")       → None (removes by name)
"""
from __future__ import annotations

from typing import Any

from .fods_worksheet import FodsWorksheet


class FodsWorksheetCollection:
    """Aspose-style collection of worksheets within a FodsDocument.

    Backed by the list of sheet dicts inside the parsed workbook data.
    """

    spec_qname = "office:spreadsheet"
    spec_fact_ref = "FACT-FODS-003"

    def __init__(self, sheets: list[dict[str, Any]]):
        self._sheets = sheets

    @property
    def count(self) -> int:
        """Return the number of worksheets in the collection."""
        return len(self._sheets)

    def __len__(self) -> int:
        return self.count

    def __getitem__(self, key: int | str) -> FodsWorksheet:
        if isinstance(key, int):
            if key < 0 or key >= len(self._sheets):
                raise IndexError(f"Worksheet index {key} out of range (count={len(self._sheets)}).")
            return FodsWorksheet(self._sheets[key])
        if isinstance(key, str):
            for s in self._sheets:
                if s.get("name") == key:
                    return FodsWorksheet(s)
            raise KeyError(f"No worksheet named '{key}'.")
        raise TypeError(f"Worksheet key must be int or str; got {type(key).__name__}")

    def __iter__(self):
        for s in self._sheets:
            yield FodsWorksheet(s)

    def add(self, name: str) -> FodsWorksheet:
        """Add a new empty worksheet with the given name.

        Raises ValueError if a worksheet with the same name already exists.
        """
        for s in self._sheets:
            if s.get("name") == name:
                raise ValueError(f"A worksheet named '{name}' already exists.")
        new_sheet: dict[str, Any] = {"name": name, "rows": []}
        self._sheets.append(new_sheet)
        return FodsWorksheet(new_sheet)

    def remove(self, name: str) -> None:
        """Remove a worksheet by name.

        Raises KeyError if no worksheet with that name exists.
        """
        for i, s in enumerate(self._sheets):
            if s.get("name") == name:
                del self._sheets[i]
                return
        raise KeyError(f"No worksheet named '{name}'.")

    def __repr__(self) -> str:
        names = [s.get("name", "") for s in self._sheets]
        return f"FodsWorksheetCollection({names!r})"
