"""Domain model for Jupyter Notebook documents."""

from __future__ import annotations

from typing import Any, ClassVar


class IpynbDocument:
    """Typed domain model wrapping a parsed Jupyter Notebook."""

    spec_qname: ClassVar[str] = "ipynb:notebook"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> IpynbDocument:
        from ipynb.ipynb_codec import load_ipynb

        return cls(load_ipynb(path))

    @property
    def raw(self) -> dict[str, Any]:
        return self._data

    @property
    def nbformat(self) -> int:
        return self._data.get("nbformat", 0)

    @property
    def nbformat_minor(self) -> int:
        return self._data.get("nbformat_minor", 0)

    @property
    def metadata(self) -> dict[str, Any]:
        return self._data.get("metadata", {})

    @property
    def cells(self) -> list[dict[str, Any]]:
        return self._data.get("cells", [])

    @property
    def cell_count(self) -> int:
        return len(self.cells)

    @property
    def is_empty(self) -> bool:
        return self.cell_count == 0

    @property
    def code_cells(self) -> list[dict[str, Any]]:
        return [c for c in self.cells if c.get("cell_type") == "code"]

    @property
    def markdown_cells(self) -> list[dict[str, Any]]:
        return [c for c in self.cells if c.get("cell_type") == "markdown"]

    @property
    def raw_cells(self) -> list[dict[str, Any]]:
        return [c for c in self.cells if c.get("cell_type") == "raw"]

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"IpynbDocument(nbformat={self.nbformat}, cells={self.cell_count})"
