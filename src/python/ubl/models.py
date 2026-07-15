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
        from ubl.ubl_codec import load_ubl

        return cls(load_ubl(path))

    @property
    def raw(self) -> dict[str, Any]:
        return self._data

    @property
    def document_type(self) -> str:
        return self._data.get("document_type", "")

    @property
    def ubl_version(self) -> str:
        return self._data.get("ubl_version", "")

    @property
    def doc_id(self) -> str:
        return self._data.get("id", "")

    @property
    def issue_date(self) -> str:
        return self._data.get("issue_date", "")

    @property
    def lines(self) -> list[dict[str, Any]]:
        return self._data.get("lines", [])

    @property
    def line_count(self) -> int:
        return len(self.lines)

    @property
    def is_empty(self) -> bool:
        return self.line_count == 0

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"UblDocument(type={self.document_type!r}, id={self.doc_id!r})"
