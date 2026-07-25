from __future__ import annotations

import json
import struct

import pytest

from format_factory.safetensors import SafeTensorsParseError, loads
from format_factory.safetensors.model import DType, TensorDescriptor

_MAX_U64 = (1 << 64) - 1


@pytest.mark.parametrize(
    ("shape", "dtype", "message"),
    [
        ((_MAX_U64 + 1,), DType.U8, "shape dimension exceeds unsigned 64-bit size"),
        ((1 << 63, 2), DType.U8, "shape element count overflows unsigned 64-bit size"),
        ((1 << 61,), DType.F64, "tensor element-bit count overflows unsigned 64-bit size"),
    ],
)
def test_model_rejects_unsigned_64_bit_size_overflow(
    shape: tuple[int, ...],
    dtype: DType,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        TensorDescriptor(
            name="overflow",
            dtype=dtype,
            shape=shape,
            data_offsets=(0, 0),
        )


@pytest.mark.parametrize(
    ("shape", "dtype", "message"),
    [
        ([_MAX_U64 + 1], "U8", "shape dimension exceeds unsigned 64-bit size"),
        ([1 << 63, 2], "U8", "shape element count overflows unsigned 64-bit size"),
        ([1 << 61], "F64", "tensor element-bit count overflows unsigned 64-bit size"),
    ],
)
def test_reader_rejects_unsigned_64_bit_size_overflow(
    shape: list[int],
    dtype: str,
    message: str,
) -> None:
    header = json.dumps(
        {
            "overflow": {
                "dtype": dtype,
                "shape": shape,
                "data_offsets": [0, 0],
            }
        },
        separators=(",", ":"),
    ).encode("utf-8")
    encoded = struct.pack("<Q", len(header)) + header

    with pytest.raises(SafeTensorsParseError, match=message):
        loads(encoded)
