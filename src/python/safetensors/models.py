"""Domain model for SafeTensors documents."""

from __future__ import annotations

from typing import Any, ClassVar


class SafetensorsDocument:
    """Typed domain model wrapping a parsed SafeTensors file."""

    spec_qname: ClassVar[str] = "safetensors:header"

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> SafetensorsDocument:
        from safetensors.safetensors_codec import load_safetensors

        return cls(load_safetensors(path))

    @property
    def raw(self) -> dict[str, Any]:
        return self._data

    @property
    def tensors(self) -> dict[str, Any]:
        return self._data.get("tensors", {})

    @property
    def metadata(self) -> dict[str, str]:
        return self._data.get("metadata", {})

    @property
    def tensor_count(self) -> int:
        return len(self.tensors)

    @property
    def tensor_names(self) -> list[str]:
        return sorted(self.tensors.keys())

    @property
    def is_empty(self) -> bool:
        return self.tensor_count == 0

    @property
    def header_size(self) -> int:
        return self._data.get("header_size", 0)

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"SafetensorsDocument(tensors={self.tensor_count})"
