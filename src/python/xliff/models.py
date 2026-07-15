"""Domain model for XLIFF documents."""

from __future__ import annotations

from typing import Any, ClassVar


class XliffDocument:
    """Typed domain model wrapping a parsed XLIFF file."""

    spec_qname: ClassVar[str] = "xliff:file"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> XliffDocument:
        """Load an XLIFF document from the file at path."""
        from xliff.xliff_codec import load_xliff

        return cls(load_xliff(path))

    @property
    def raw(self) -> dict[str, Any]:
        """Return the underlying parsed data dictionary."""
        return self._data

    @property
    def version(self) -> str:
        """Return the XLIFF format version string."""
        return self._data.get("version", "")

    @property
    def source_language(self) -> str:
        """Return the source language code."""
        return self._data.get("source_language", "")

    @property
    def target_language(self) -> str:
        """Return the target language code."""
        return self._data.get("target_language", "")

    @property
    def files(self) -> list[dict[str, Any]]:
        """Return the list of XLIFF file elements."""
        return self._data.get("files", [])

    @property
    def file_count(self) -> int:
        """Return the number of XLIFF file elements."""
        return len(self.files)

    @property
    def units(self) -> list[dict[str, Any]]:
        """Return all translation units across all files."""
        result: list[dict[str, Any]] = []
        for f in self.files:
            result.extend(f.get("units", []))
        return result

    @property
    def unit_count(self) -> int:
        """Return the total number of translation units."""
        return len(self.units)

    @property
    def is_empty(self) -> bool:
        """Return True if the document contains no translation units."""
        return self.unit_count == 0

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"XliffDocument(version={self.version!r}, units={self.unit_count})"
