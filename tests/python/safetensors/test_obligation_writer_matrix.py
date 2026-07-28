from __future__ import annotations

import struct

import pytest

from format_factory.safetensors import (
    DType,
    SafeTensorsDocument,
    SafeTensorsWriteError,
    TensorDescriptor,
    dumps,
    loads,
)


def _dtype_case(dtype: DType) -> tuple[int, bytes]:
    elements = 2 if dtype.bits == 4 else 4 if dtype.bits == 6 else 1
    byte_count = elements * dtype.bits // 8
    return elements, bytes(range(byte_count))


@pytest.mark.parametrize("dtype", list(DType))
def test_every_dtype_writes_deterministically_and_roundtrips(dtype: DType) -> None:
    elements, payload = _dtype_case(dtype)
    descriptor = TensorDescriptor(
        name="value",
        dtype=dtype,
        shape=(elements,),
        data_offsets=(0, len(payload)),
    )
    with SafeTensorsDocument(tensors={"value": descriptor}, payload=payload) as document:
        first = dumps(document)
        second = dumps(document)

    assert first == second
    with loads(first) as rebuilt:
        assert rebuilt.tensors["value"].dtype is dtype
        assert rebuilt.tensors["value"].shape == (elements,)
        assert bytes(rebuilt.tensor_bytes("value")) == payload


@pytest.mark.parametrize(
    ("shape", "payload"),
    [
        ((), b"\0\0\x80?"),
        ((2, 0), b""),
    ],
    ids=["scalar", "empty"],
)
def test_scalar_and_empty_tensor_writes_preserve_semantics(
    shape: tuple[int, ...],
    payload: bytes,
) -> None:
    descriptor = TensorDescriptor(
        name="value",
        dtype=DType.F32,
        shape=shape,
        data_offsets=(0, len(payload)),
    )
    with SafeTensorsDocument(tensors={"value": descriptor}, payload=payload) as document:
        rebuilt_bytes = dumps(document)

    with loads(rebuilt_bytes) as rebuilt:
        assert rebuilt.tensors["value"].shape == shape
        assert bytes(rebuilt.tensor_bytes("value")) == payload


def test_metadata_output_is_deterministic() -> None:
    descriptor = TensorDescriptor("value", DType.U8, (1,), (0, 1))
    with SafeTensorsDocument(
        tensors={"value": descriptor},
        metadata={"z": "last", "a": "first"},
        payload=b"\x01",
    ) as document:
        encoded = dumps(document)
        assert encoded == dumps(document)

    header_size = struct.unpack("<Q", encoded[:8])[0]
    header = encoded[8 : 8 + header_size]
    assert header.index(b'"a":"first"') < header.index(b'"z":"last"')
    with loads(encoded) as rebuilt:
        assert dict(rebuilt.metadata) == {"a": "first", "z": "last"}


def test_writer_rejects_inconsistent_payload_extent() -> None:
    descriptor = TensorDescriptor("value", DType.U8, (1,), (0, 1))
    with SafeTensorsDocument(tensors={"value": descriptor}, payload=b"") as document:
        with pytest.raises(SafeTensorsWriteError, match="payload bytes"):
            dumps(document)
