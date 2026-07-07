"""
ODF spec element: table:table-cell

Spec ref: ODF 1.3 §9.5 — Table Cell Elements
Fact ref: FACT-FODS-006
QName: table:table-cell
Namespace: urn:oasis:names:tc:opendocument:xmlns:table:1.0
Canonical class: Table.TableCell
"""

from __future__ import annotations
from typing import Any


class TableCell:
    """Canonical spec-shaped class for table:table-cell in FODS context.

    A cell within table:table-row. Has office:value-type, office:value,
    and table:style-name attributes. Contains text:p children for string/formula cells.

    TC-W1-FODS-PY-001: this class now holds cell data so FodsCell can delegate to it.
    Facade: FodsCell delegates to this via spec_qname.
    """

    spec_qname = "table:table-cell"
    spec_fact_ref = "FACT-FODS-006"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    local_name = "table-cell"
    facade_names = ["FodsCell"]

    def __init__(self, data: dict[str, Any] | None = None):
        self._data: dict[str, Any] = data or {}

    @property
    def value(self) -> Any:
        """Return the cell's typed value (float, int, str, date, bool, or None)."""
        return self._data.get("value")

    @value.setter
    def value(self, v: Any) -> None:
        """Set the cell's typed value."""
        self._data["value"] = v

    @property
    def value_type(self) -> str:
        """Return the office:value-type attribute string (e.g. 'float', 'string')."""
        return self._data.get("value_type", "")

    @property
    def text(self) -> str:
        """Return the display text from the text:p child element."""
        return self._data.get("text", "")

    @property
    def formula(self) -> str | None:
        """Return the table:formula attribute string, or None if not a formula cell."""
        return self._data.get("formula")

    @property
    def repeated(self) -> int:
        """Return the table:number-columns-repeated count (default 1)."""
        return self._data.get("repeated", 1)

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the internal data dictionary."""
        return dict(self._data)
