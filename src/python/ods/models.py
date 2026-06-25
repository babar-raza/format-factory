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
from typing import Any, ClassVar


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

    def get_sheet(self, index: int) -> Any:
        """Return the OdsSheet at the given index."""
        return self._parsed.sheets[index]

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
