"""
ipynb structural element: ipynb:notebook

Spec ref: Jupyter nbformat v4.5 Specification
Fact ref: FACT-IPYNB-001
QName: ipynb:notebook
Canonical class: Notebook
Facade: IpynbNotebook

architecture_only: this class is a spec-shaped scaffold. It wraps a parsed
notebook dict and exposes read-only properties for the required top-level
keys (nbformat, nbformat_minor, metadata, cells). No parsing or write
behavior lives here — that is owned by ``ipynb_codec``.
"""
from __future__ import annotations

from typing import Any


class Notebook:
    """Canonical spec-shaped class for ipynb:notebook (root JSON document)."""

    spec_qname = "ipynb:notebook"
    spec_fact_ref = "FACT-IPYNB-001"
    namespace_uri = "urn:format:ipynb:4.5"
    local_name = "notebook"
    facade_names = ["IpynbNotebook"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def nbformat(self) -> int:
        """Return the notebook format major version number."""
        return int(self._data.get("nbformat", 0))

    @property
    def nbformat_minor(self) -> int:
        """Return the notebook format minor version number."""
        return int(self._data.get("nbformat_minor", 0))

    @property
    def metadata(self) -> dict[str, Any]:
        """Return the notebook-level metadata dictionary."""
        return self._data.get("metadata", {})

    @property
    def cells(self) -> list[dict[str, Any]]:
        """Return the list of all cell dictionaries."""
        return self._data.get("cells", [])

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Notebook(nbformat={self.nbformat}, cells={len(self.cells)})"
