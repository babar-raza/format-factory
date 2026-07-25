from __future__ import annotations

import importlib
import sys
from typing import Any

from ..model import DType, SafeTensorsDocument


_TORCH_DTYPE_NAMES = {
    DType.BOOL: "bool",
    DType.U8: "uint8",
    DType.I8: "int8",
    DType.F8_E5M2: "float8_e5m2",
    DType.F8_E4M3: "float8_e4m3fn",
    DType.F8_E8M0: "float8_e8m0fnu",
    DType.F8_E4M3FNUZ: "float8_e4m3fnuz",
    DType.F8_E5M2FNUZ: "float8_e5m2fnuz",
    DType.I16: "int16",
    DType.U16: "uint16",
    DType.F16: "float16",
    DType.BF16: "bfloat16",
    DType.I32: "int32",
    DType.U32: "uint32",
    DType.F32: "float32",
    DType.C64: "complex64",
    DType.F64: "float64",
    DType.I64: "int64",
    DType.U64: "uint64",
}


def to_torch(
    document: SafeTensorsDocument,
    name: str,
    *,
    copy: bool = True,
    device: Any = None,
) -> Any:
    """Create a safe mutable PyTorch tensor and optionally move it to ``device``.

    PyTorch has no read-only tensor view. A zero-copy view over SafeTensors'
    read-only payload would therefore expose undefined writes (and may target a
    read-only memory map), so this adapter deliberately requires ``copy=True``.
    The initial tensor is CPU-backed by an independent writable bytearray; a
    non-CPU ``device`` then uses PyTorch's normal transfer semantics.
    """

    if not copy:
        raise ValueError(
            "PyTorch tensors are mutable; copy=False is unsafe for a read-only "
            "SafeTensors payload. Pass copy=True."
        )
    if sys.byteorder != "little":
        raise RuntimeError(
            "the PyTorch adapter requires a little-endian host for exact "
            "SafeTensors byte interpretation"
        )
    torch: Any = importlib.import_module("torch")

    descriptor = document.tensors[name]
    dtype_name = _TORCH_DTYPE_NAMES.get(descriptor.dtype)
    dtype = getattr(torch, dtype_name, None) if dtype_name is not None else None
    if dtype is None:
        raise TypeError(
            f"installed PyTorch does not expose an exact dtype for {descriptor.dtype}"
        )

    if descriptor.element_count == 0:
        tensor = torch.empty(descriptor.shape, dtype=dtype)
    else:
        owned = bytearray(document.tensor_bytes(name))
        tensor = torch.frombuffer(
            owned,
            dtype=dtype,
            count=descriptor.element_count,
        ).reshape(descriptor.shape)
    if device is not None:
        tensor = tensor.to(device=device)
    return tensor
