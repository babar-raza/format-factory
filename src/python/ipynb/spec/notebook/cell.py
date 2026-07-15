"""
ipynb structural element: ipynb:cell

Spec ref: Jupyter nbformat v4.5 Specification
Fact ref: FACT-IPYNB-002
QName: ipynb:cell
Canonical class: Cell
Facade: IpynbCell

architecture_only: this class is a spec-shaped scaffold. It wraps a single
cell dict and exposes read-only properties for cell_type, source,
metadata, outputs, and execution_count. No parsing or write behavior
lives here — that is owned by ``ipynb_codec``.
"""
from __future__ import annotations

from typing import Any


class Cell:
    """Canonical spec-shaped class for ipynb:cell (a single notebook cell)."""

    spec_qname = "ipynb:cell"
    spec_fact_ref = "FACT-IPYNB-002"
    namespace_uri = "urn:format:ipynb:4.5"
    local_name = "cell"
    facade_names = ["IpynbCell"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def cell_type(self) -> str:
        """Return the cell type: one of 'code', 'markdown', or 'raw'."""
        return self._data.get("cell_type", "raw")

    @property
    def source(self) -> Any:
        """Return the cell source, a string or a list of line strings."""
        return self._data.get("source", "")

    @property
    def metadata(self) -> dict[str, Any]:
        """Return the cell-level metadata dictionary."""
        return self._data.get("metadata", {})

    @property
    def outputs(self) -> list[dict[str, Any]]:
        """Return the list of output dicts (code cells only; empty otherwise)."""
        return self._data.get("outputs", [])

    @property
    def execution_count(self) -> int | None:
        """Return the execution count for code cells, or None if not executed."""
        return self._data.get("execution_count")

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Cell(cell_type={self.cell_type!r})"
