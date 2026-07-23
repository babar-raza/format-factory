from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

from format_factory.safetensors import (
    DType,
    SafeTensorsDocument,
    SafeTensorsParseError,
    TensorDescriptor,
    dumps,
    load,
    loads,
    probe,
    validate,
)


def make_file(header: dict[str, object], payload: bytes = b"") -> bytes:
    raw = json.dumps(header, separators=(",", ":")).encode()
    return struct.pack("<Q", len(raw)) + raw + payload


def test_scalar_roundtrip_is_deterministic() -> None:
    raw = make_file(
        {"x": {"dtype": "F32", "shape": [], "data_offsets": [0, 4]}},
        b"\0\0\x80?",
    )
    with loads(raw) as document:
        first = dumps(document)
        second = dumps(document)
    assert first == second
    with loads(first) as rebuilt:
        assert rebuilt.tensors["x"].shape == ()
        assert bytes(rebuilt.tensor_bytes("x")) == b"\0\0\x80?"


def test_empty_tensor_is_valid() -> None:
    raw = make_file({"empty": {"dtype": "I32", "shape": [2, 0], "data_offsets": [0, 0]}})
    with loads(raw) as document:
        assert document.tensors["empty"].byte_length == 0


@pytest.mark.parametrize("dtype", list(DType))
def test_complete_dtype_inventory(dtype: DType) -> None:
    elements = 2 if dtype.bits == 4 else 4 if dtype.bits == 6 else 1
    byte_count = elements * dtype.bits // 8
    raw = make_file(
        {"x": {"dtype": dtype.value, "shape": [elements], "data_offsets": [0, byte_count]}},
        bytes(byte_count),
    )
    with loads(raw) as document:
        assert document.tensors["x"].dtype is dtype


def test_subbyte_misalignment_rejected() -> None:
    raw = make_file({"x": {"dtype": "F4", "shape": [1], "data_offsets": [0, 0]}})
    with pytest.raises(SafeTensorsParseError, match="byte boundary"):
        loads(raw)


def test_duplicate_key_rejected() -> None:
    header = b'{"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]},"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]}}'
    raw = struct.pack("<Q", len(header)) + header + b"\0"
    with pytest.raises(SafeTensorsParseError, match="duplicate"):
        loads(raw)


@pytest.mark.parametrize(
    "offsets,payload,match",
    [
        ([1, 2], b"\0\0", "hole"),
        ([0, 2], b"\0", "beyond"),
        ([0, 0], b"\0", "spans"),
    ],
)
def test_unsafe_offsets_rejected(offsets: list[int], payload: bytes, match: str) -> None:
    raw = make_file({"x": {"dtype": "U8", "shape": [1], "data_offsets": offsets}}, payload)
    with pytest.raises(SafeTensorsParseError, match=match):
        loads(raw)


def test_trailing_polyglot_data_rejected() -> None:
    raw = make_file({"x": {"dtype": "U8", "shape": [1], "data_offsets": [0, 1]}}, b"\0extra")
    with pytest.raises(SafeTensorsParseError, match="cover"):
        loads(raw)


def test_metadata_must_be_strings() -> None:
    with pytest.raises(SafeTensorsParseError, match="string-to-string"):
        loads(make_file({"__metadata__": {"bad": 1}}))


def test_unknown_tensor_fields_preserved() -> None:
    raw = make_file(
        {"x": {"dtype": "U8", "shape": [1], "data_offsets": [0, 1], "vendor": "ok"}},
        b"\x01",
    )
    with loads(raw, mode="preservation") as document:
        rebuilt = dumps(document)
    assert b'"vendor":"ok"' in rebuilt


def test_memory_mapped_path(tmp_path: Path) -> None:
    path = tmp_path / "x.safetensors"
    path.write_bytes(make_file({"x": {"dtype": "U8", "shape": [1], "data_offsets": [0, 1]}}, b"\x07"))
    with load(path) as document:
        assert bytes(document.tensor_bytes("x")) == b"\x07"


def test_probe_and_validation() -> None:
    valid = make_file({})
    assert probe(valid)
    assert validate(valid)
    assert not probe(b"not a tensor")
    assert not validate(b"not a tensor")


def test_model_validation_rejects_hole() -> None:
    document = SafeTensorsDocument(
        tensors={
            "x": TensorDescriptor("x", DType.U8, (1,), (1, 2)),
        },
        payload=b"\0\0",
    )
    assert not validate(document)


def test_no_top_level_namespace_in_production_tree() -> None:
    package_root = Path(__file__).parents[3] / "src" / "python" / "safetensors" / "src"
    assert not (package_root / "safetensors").exists()
    assert not (package_root / "format_factory" / "__init__.py").exists()
