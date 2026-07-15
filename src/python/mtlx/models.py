"""Domain model for MaterialX documents."""

from __future__ import annotations

from typing import Any, ClassVar


class MtlxDocument:
    """Typed domain model wrapping a parsed MaterialX file."""

    spec_qname: ClassVar[str] = "materialx:material"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> MtlxDocument:
        from mtlx.mtlx_codec import load_mtlx

        return cls(load_mtlx(path))

    @property
    def raw(self) -> dict[str, Any]:
        return self._data

    @property
    def version(self) -> str:
        return self._data.get("version", "")

    @property
    def materials(self) -> list[dict[str, Any]]:
        return self._data.get("materials", [])

    @property
    def node_graphs(self) -> list[dict[str, Any]]:
        return self._data.get("node_graphs", [])

    @property
    def material_count(self) -> int:
        return len(self.materials)

    @property
    def node_graph_count(self) -> int:
        return len(self.node_graphs)

    @property
    def is_empty(self) -> bool:
        return self.material_count == 0 and self.node_graph_count == 0

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"MtlxDocument(version={self.version!r}, materials={self.material_count})"
