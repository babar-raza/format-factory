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
        """Load a Jupyter Notebook document from the file at path."""
        from ipynb.ipynb_codec import load_ipynb

        return cls(load_ipynb(path))

    @property
    def raw(self) -> dict[str, Any]:
        """Return the underlying parsed data dictionary."""
        return self._data

    @property
    def nbformat(self) -> int:
        """Return the notebook format version number."""
        return self._data.get("nbformat", 0)

    @property
    def nbformat_minor(self) -> int:
        """Return the notebook format minor version number."""
        return self._data.get("nbformat_minor", 0)

    @property
    def metadata(self) -> dict[str, Any]:
        """Return the notebook-level metadata dictionary."""
        return self._data.get("metadata", {})

    @property
    def cells(self) -> list[dict[str, Any]]:
        """Return the list of all cell dictionaries."""
        return self._data.get("cells", [])

    @property
    def cell_count(self) -> int:
        """Return the total number of cells."""
        return len(self.cells)

    @property
    def is_empty(self) -> bool:
        """Return True if the document contains no cells."""
        return self.cell_count == 0

    @property
    def code_cells(self) -> list[dict[str, Any]]:
        """Return cells with cell_type 'code'."""
        return [c for c in self.cells if c.get("cell_type") == "code"]

    @property
    def markdown_cells(self) -> list[dict[str, Any]]:
        """Return cells with cell_type 'markdown'."""
        return [c for c in self.cells if c.get("cell_type") == "markdown"]

    @property
    def raw_cells(self) -> list[dict[str, Any]]:
        """Return cells with cell_type 'raw'."""
        return [c for c in self.cells if c.get("cell_type") == "raw"]

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    # --- Structural mutation API (FACT-IPYNB-104) ---------------------------

    def add_cell(
        self,
        cell_type: str = "code",
        source: Any = "",
        metadata: dict[str, Any] | None = None,
        index: int | None = None,
    ) -> dict[str, Any]:
        """Create a new cell and insert it into this document.

        The new cell is automatically given a valid, notebook-unique id
        (via ``ipynb_codec.ensure_cell_id``) — callers never need to
        invent one themselves. If ``index`` is None the cell is appended;
        otherwise it is inserted at that position (same semantics as
        ``list.insert``). Returns the newly created cell dict, which is
        already present in ``self.cells``.
        """
        from ipynb.ipynb_codec import ensure_cell_id

        used_ids = {c["id"] for c in self.cells if isinstance(c.get("id"), str)}
        new_cell: dict[str, Any] = {
            "cell_type": cell_type,
            "source": source,
            "metadata": dict(metadata) if metadata is not None else {},
        }
        if cell_type == "code":
            new_cell["outputs"] = []
            new_cell["execution_count"] = None
        ensure_cell_id(new_cell, used_ids)

        cells = self._data.setdefault("cells", [])
        if index is None:
            cells.append(new_cell)
        else:
            cells.insert(index, new_cell)
        return new_cell

    def remove_cell(self, index: int) -> dict[str, Any]:
        """Remove and return the cell at ``index``.

        Raises IndexError if ``index`` is out of range. The remaining
        cells are left in their original order/content, unaffected.
        """
        cells = self._data.get("cells", [])
        return cells.pop(index)

    def clear_outputs(self, index: int) -> dict[str, Any]:
        """Clear outputs on the code cell at ``index``.

        Sets ``outputs`` to ``[]`` and resets ``execution_count`` to
        ``None`` (the nbformat convention for an unexecuted cell). Raises
        ValueError if the cell at ``index`` is not a code cell. Returns
        the mutated cell dict.
        """
        cells = self._data.get("cells", [])
        cell = cells[index]
        if cell.get("cell_type") != "code":
            raise ValueError(
                f"Cell at index {index} is not a code cell "
                f"(cell_type={cell.get('cell_type')!r})"
            )
        cell["outputs"] = []
        cell["execution_count"] = None
        return cell

    def __repr__(self) -> str:
        return f"IpynbDocument(nbformat={self.nbformat}, cells={self.cell_count})"
