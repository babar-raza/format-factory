"""Domain model for NRRD documents."""

from __future__ import annotations

from typing import Any, ClassVar


class NrrdDocument:
    """Typed domain model wrapping a parsed NRRD file."""

    spec_qname: ClassVar[str] = "nrrd:header"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> NrrdDocument:
        from nrrd.nrrd_codec import load_nrrd

        return cls(load_nrrd(path))

    @property
    def raw(self) -> dict[str, Any]:
        return self._data

    @property
    def version(self) -> int:
        return self._data.get("version", 0)

    @property
    def header(self) -> dict[str, str]:
        return self._data.get("header", {})

    @property
    def data_size(self) -> int:
        return self._data.get("data_size", 0)

    @property
    def dimension(self) -> int:
        return int(self.header.get("dimension", "0"))

    @property
    def encoding(self) -> str:
        return self.header.get("encoding", "raw")

    @property
    def nrrd_type(self) -> str:
        return self.header.get("type", "")

    @property
    def sizes(self) -> list[int]:
        sizes_str = self.header.get("sizes", "")
        if not sizes_str:
            return []
        return [int(s) for s in sizes_str.split()]

    @property
    def is_empty(self) -> bool:
        return self.data_size == 0

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"NrrdDocument(version={self.version}, encoding={self.encoding!r})"
