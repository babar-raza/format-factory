"""
SafeTensors structural element: safetensors:tensor

Spec ref: Hugging Face SafeTensors Specification v0.4 — Header format
Fact ref: FACT-SAFETENSORS-002
QName: safetensors:tensor
Canonical class: Tensor
Facade: SafetensorsTensor
"""
from __future__ import annotations
from typing import Any


class Tensor:
    """Canonical spec-shaped class for safetensors:tensor (dtype/shape/data_offsets descriptor)."""

    spec_qname = "safetensors:tensor"
    spec_fact_ref = "FACT-SAFETENSORS-002"
    namespace_uri = "urn:format:safetensors:0.4"
    local_name = "tensor"
    facade_names = ["SafetensorsTensor"]

    VALID_DTYPES = (
        "F16", "BF16", "F32", "F64",
        "I8", "I16", "I32", "I64",
        "U8", "U16", "U32", "U64",
        "BOOL",
    )

    def __init__(self, name: str, data: dict[str, Any]) -> None:
        """Wrap one tensor descriptor entry (dtype/shape/data_offsets) by name."""
        self._name = name
        self._data = data

    @property
    def name(self) -> str:
        """Return the tensor's key in the header JSON object."""
        return self._name

    @property
    def dtype(self) -> str:
        """Return the tensor's dtype string (e.g. F32, I8, BOOL) (FACT-SAFETENSORS-002)."""
        return str(self._data.get("dtype", "unknown"))

    @property
    def shape(self) -> list[int]:
        """Return the tensor's shape as a list of dimension sizes (FACT-SAFETENSORS-002)."""
        return list(self._data.get("shape", []))

    @property
    def data_offsets(self) -> list[int]:
        """Return the [begin, end] byte offsets into the data section (FACT-SAFETENSORS-003)."""
        return list(self._data.get("data_offsets", [0, 0]))

    @property
    def byte_length(self) -> int:
        """Return the tensor's byte span (data_offsets[1] - data_offsets[0])."""
        offsets = self.data_offsets
        if len(offsets) != 2:
            return 0
        return max(0, offsets[1] - offsets[0])

    def to_dict(self) -> dict[str, Any]:
        """Return the tensor descriptor as a dict, including its name."""
        return {"name": self._name, **self._data}

    def __repr__(self) -> str:
        return f"Tensor(name={self._name!r}, dtype={self.dtype}, shape={self.shape})"
