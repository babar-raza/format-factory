from __future__ import annotations

import importlib
from typing import Any

from ..model import DType, SafeTensorsDocument


def to_numpy(document: SafeTensorsDocument, name: str, *, copy: bool = False) -> Any:
    """Expose a tensor as a C-order NumPy array.

    ``copy=False`` returns a read-only view borrowed from the document payload,
    so the document must remain open while the array is used. ``copy=True``
    returns an independent writable C-order array. Dtypes without an exact
    NumPy storage dtype are rejected instead of being silently reinterpreted.
    """

    np: Any = importlib.import_module("numpy")

    descriptor = document.tensors[name]
    dtype_map = {
        DType.BOOL: np.dtype("?"),
        DType.U8: np.dtype("u1"),
        DType.I8: np.dtype("i1"),
        DType.I16: np.dtype("<i2"),
        DType.U16: np.dtype("<u2"),
        DType.F16: np.dtype("<f2"),
        DType.I32: np.dtype("<i4"),
        DType.U32: np.dtype("<u4"),
        DType.F32: np.dtype("<f4"),
        DType.C64: np.dtype("<c8"),
        DType.F64: np.dtype("<f8"),
        DType.I64: np.dtype("<i8"),
        DType.U64: np.dtype("<u8"),
    }
    if descriptor.dtype not in dtype_map:
        raise TypeError(f"NumPy adapter does not natively expose {descriptor.dtype}")
    result = np.frombuffer(document.tensor_bytes(name), dtype=dtype_map[descriptor.dtype])
    result = result.reshape(descriptor.shape)
    if copy:
        return result.copy(order="C")
    result.setflags(write=False)
    return result
