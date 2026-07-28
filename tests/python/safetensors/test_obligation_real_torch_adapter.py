from __future__ import annotations

import json
import struct

import pytest

from format_factory.safetensors import loads
from format_factory.safetensors.adapters import to_torch

torch = pytest.importorskip("torch")


def _single_tensor(dtype: str, payload: bytes, *, shape: list[int]) -> bytes:
    header = json.dumps(
        {
            "value": {
                "dtype": dtype,
                "shape": shape,
                "data_offsets": [0, len(payload)],
            }
        },
        separators=(",", ":"),
    ).encode("utf-8")
    return struct.pack("<Q", len(header)) + header + payload


@pytest.mark.parametrize(
    ("format_dtype", "torch_dtype_name", "payload"),
    [
        ("BOOL", "bool", b"\x01"),
        ("U8", "uint8", b"\xff"),
        ("I8", "int8", b"\xfe"),
        ("F8_E5M2", "float8_e5m2", b"\x00"),
        ("F8_E4M3", "float8_e4m3fn", b"\x00"),
        ("F8_E8M0", "float8_e8m0fnu", b"\x00"),
        ("F8_E4M3FNUZ", "float8_e4m3fnuz", b"\x00"),
        ("F8_E5M2FNUZ", "float8_e5m2fnuz", b"\x00"),
        ("I16", "int16", b"\xfe\xff"),
        ("U16", "uint16", b"\xfe\xff"),
        ("F16", "float16", b"\x00\x3c"),
        ("BF16", "bfloat16", b"\x80\x3f"),
        ("I32", "int32", b"\xfc\xff\xff\xff"),
        ("U32", "uint32", b"\xfc\xff\xff\xff"),
        ("F32", "float32", b"\x00\x00\x80\x3f"),
        ("C64", "complex64", b"\x00\x00\x80\x3f\x00\x00\x00\xc0"),
        ("F64", "float64", b"\x00\x00\x00\x00\x00\x00\xf0\x3f"),
        ("I64", "int64", b"\xf8\xff\xff\xff\xff\xff\xff\xff"),
        ("U64", "uint64", b"\xf8\xff\xff\xff\xff\xff\xff\xff"),
    ],
)
def test_real_torch_exposes_every_declared_exact_adapter_dtype(
    format_dtype: str,
    torch_dtype_name: str,
    payload: bytes,
) -> None:
    with loads(_single_tensor(format_dtype, payload, shape=[1])) as document:
        tensor = to_torch(document, "value", device="cpu")

    assert isinstance(tensor, torch.Tensor)
    assert tensor.dtype is getattr(torch, torch_dtype_name)
    assert tensor.shape == (1,)
    assert tensor.device.type == "cpu"
    assert bytes(tensor.contiguous().view(torch.uint8).tolist()) == payload


def test_real_torch_tensor_owns_a_safe_mutable_copy() -> None:
    raw = _single_tensor("U8", b"\x01\x02", shape=[2])
    with loads(raw) as document:
        tensor = to_torch(document, "value", copy=True)
    tensor[0] = 9

    assert tensor.tolist() == [9, 2]
    assert raw.endswith(b"\x01\x02")


def test_real_torch_rejects_unsafe_zero_copy() -> None:
    with loads(_single_tensor("U8", b"\x01", shape=[1])) as document:
        with pytest.raises(ValueError, match="copy=True"):
            to_torch(document, "value", copy=False)


def test_real_torch_constructs_empty_tensor_with_exact_shape_and_dtype() -> None:
    with loads(_single_tensor("F32", b"", shape=[2, 0, 3])) as document:
        tensor = to_torch(document, "value")

    assert tensor.dtype is torch.float32
    assert tensor.shape == (2, 0, 3)
    assert tensor.numel() == 0


@pytest.mark.parametrize("dtype", ["F4", "F6_E2M3", "F6_E3M2"])
def test_real_torch_rejects_subbyte_types_without_silent_reinterpretation(
    dtype: str,
) -> None:
    with loads(_single_tensor(dtype, b"", shape=[0])) as document:
        with pytest.raises(TypeError, match="does not expose an exact dtype"):
            to_torch(document, "value")
