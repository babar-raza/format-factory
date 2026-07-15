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
        """Load a SafeTensors document from the file at path."""
        from safetensors.safetensors_codec import load_safetensors

        return cls(load_safetensors(path))

    @property
    def raw(self) -> dict[str, Any]:
        """Return the underlying parsed data dictionary."""
        return self._data

    @property
    def tensors(self) -> dict[str, Any]:
        """Return the tensor metadata dict keyed by tensor name."""
        return self._data.get("tensors", {})

    @property
    def metadata(self) -> dict[str, str]:
        """Return the file-level metadata dictionary."""
        return self._data.get("metadata", {})

    @property
    def tensor_count(self) -> int:
        """Return the number of tensors in the file."""
        return len(self.tensors)

    @property
    def tensor_names(self) -> list[str]:
        """Return the sorted list of tensor names."""
        return sorted(self.tensors.keys())

    @property
    def is_empty(self) -> bool:
        """Return True if the file contains no tensors."""
        return self.tensor_count == 0

    @property
    def header_size(self) -> int:
        """Return the size of the binary header in bytes."""
        return self._data.get("header_size", 0)

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def get_tensor_bytes(self, name: str) -> bytes:
        """Return the real byte payload for tensor `name` (FACT-SAFETENSORS-101)."""
        from safetensors.safetensors_codec import get_tensor_bytes as _get_tensor_bytes

        return _get_tensor_bytes(self._data, name)

    def get_tensor(self, name: str) -> Any:
        """Decode tensor `name` into a numpy.ndarray (FACT-SAFETENSORS-102)."""
        from safetensors.safetensors_codec import get_tensor as _get_tensor

        return _get_tensor(self._data, name)

    def __repr__(self) -> str:
        return f"SafetensorsDocument(tensors={self.tensor_count})"
