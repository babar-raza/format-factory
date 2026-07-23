"""Pure Jupyter Notebook model objects; this module performs no I/O."""

from __future__ import annotations

from typing import Any, ClassVar, cast


class Cell:
    spec_qname: ClassVar[str] = "ipynb:cell"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def cell_type(self) -> str:
        return str(self._data.get("cell_type", "raw"))

    @property
    def id(self) -> str | None:
        value = self._data.get("id")
        return value if isinstance(value, str) else None

    @property
    def source(self) -> str | list[str]:
        value = self._data.get("source", "")
        return value if isinstance(value, (str, list)) else ""

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._data.get("metadata", {}))

    @property
    def outputs(self) -> list[dict[str, Any]]:
        return list(self._data.get("outputs", []))

    @property
    def attachments(self) -> dict[str, Any]:
        return dict(self._data.get("attachments", {}))

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)


class Output:
    spec_qname: ClassVar[str] = "ipynb:output"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def output_type(self) -> str:
        return str(self._data.get("output_type", ""))

    @property
    def data(self) -> dict[str, Any]:
        return dict(self._data.get("data", {}))

    def get_representation(self, mime_type: str) -> Any:
        return self._data.get("data", {}).get(mime_type)

    def add_representation(self, mime_type: str, value: Any) -> None:
        self._data.setdefault("data", {})[mime_type] = value

    def remove_representation(self, mime_type: str) -> bool:
        bundle = self._data.get("data")
        if isinstance(bundle, dict) and mime_type in bundle:
            del bundle[mime_type]
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)


class IpynbDocument:
    """Mutable typed view over a preservation-oriented notebook mapping."""

    spec_qname: ClassVar[str] = "ipynb:notebook"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> "IpynbDocument":
        from ..codec.reader import load

        return load(path, mode="preservation")

    @property
    def raw(self) -> dict[str, Any]:
        return self._data

    @property
    def nbformat(self) -> int:
        return int(self._data.get("nbformat", 0))

    @property
    def nbformat_minor(self) -> int:
        return int(self._data.get("nbformat_minor", 0))

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._data.get("metadata", {}))

    @property
    def cells(self) -> list[dict[str, Any]]:
        cells = self._data.setdefault("cells", [])
        if not isinstance(cells, list):
            raise TypeError("notebook cells must be a list")
        return cast(list[dict[str, Any]], cells)

    @property
    def cell_count(self) -> int:
        return len(self.cells)

    @property
    def is_empty(self) -> bool:
        return not self.cells

    @property
    def code_cells(self) -> list[dict[str, Any]]:
        return [cell for cell in self.cells if cell.get("cell_type") == "code"]

    @property
    def markdown_cells(self) -> list[dict[str, Any]]:
        return [cell for cell in self.cells if cell.get("cell_type") == "markdown"]

    @property
    def raw_cells(self) -> list[dict[str, Any]]:
        return [cell for cell in self.cells if cell.get("cell_type") == "raw"]

    def add_cell(
        self,
        cell_type: str = "code",
        source: str | list[str] = "",
        metadata: dict[str, Any] | None = None,
        index: int | None = None,
    ) -> dict[str, Any]:
        from ..codec.reader import ensure_cell_id

        used_ids = {
            cell["id"] for cell in self.cells if isinstance(cell.get("id"), str)
        }
        cell: dict[str, Any] = {
            "cell_type": cell_type,
            "source": source,
            "metadata": dict(metadata or {}),
        }
        if cell_type == "code":
            cell.update(outputs=[], execution_count=None)
        ensure_cell_id(cell, used_ids)
        if index is None:
            self.cells.append(cell)
        else:
            self.cells.insert(index, cell)
        return cell

    def remove_cell(self, index: int) -> dict[str, Any]:
        removed: dict[str, Any] = self.cells.pop(index)
        return removed

    def clear_outputs(self, index: int) -> dict[str, Any]:
        cell = self.cells[index]
        if cell.get("cell_type") != "code":
            raise ValueError(f"cell at index {index} is not a code cell")
        cell["outputs"] = []
        cell["execution_count"] = None
        return cell

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"IpynbDocument(nbformat={self.nbformat}, cells={self.cell_count})"


Document = IpynbDocument
