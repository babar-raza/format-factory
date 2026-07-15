"""Domain model for UBL documents."""

from __future__ import annotations

from typing import Any, ClassVar


class UblDocument:
    """Typed domain model wrapping a parsed UBL document."""

    spec_qname: ClassVar[str] = "ubl:invoice"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> UblDocument:
        """Load a UBL document from the file at path."""
        from ubl.ubl_codec import load_ubl

        return cls(load_ubl(path))

    @property
    def raw(self) -> dict[str, Any]:
        """Return the underlying parsed data dictionary."""
        return self._data

    @property
    def document_type(self) -> str:
        """Return the UBL document type identifier."""
        return self._data.get("document_type", "")

    @property
    def ubl_version(self) -> str:
        """Return the UBL specification version string."""
        return self._data.get("ubl_version", "")

    @property
    def doc_id(self) -> str:
        """Return the document ID value."""
        return self._data.get("id", "")

    @property
    def issue_date(self) -> str:
        """Return the document issue date string."""
        return self._data.get("issue_date", "")

    @property
    def lines(self) -> list[dict[str, Any]]:
        """Return the list of document line items."""
        return self._data.get("lines", [])

    @property
    def line_count(self) -> int:
        """Return the number of line items."""
        return len(self.lines)

    @property
    def is_empty(self) -> bool:
        """Return True if the document contains no line items."""
        return self.line_count == 0

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"UblDocument(type={self.document_type!r}, id={self.doc_id!r})"
